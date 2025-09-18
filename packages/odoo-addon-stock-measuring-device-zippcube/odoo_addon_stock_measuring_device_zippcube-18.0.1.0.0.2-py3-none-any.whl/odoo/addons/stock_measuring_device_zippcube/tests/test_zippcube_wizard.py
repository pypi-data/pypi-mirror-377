# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form

from odoo.addons.component.tests.common import TransactionComponentCase


class TestZippcubeWizard(TransactionComponentCase):
    @staticmethod
    def get_measure_result(length, width, height, weight):
        return {
            "length": length,
            "width": width,
            "height": height,
            "weight": weight,
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.device_obj = cls.env["measuring.device"]
        cls.cs_wizard = cls.env["measuring.wizard"]
        PackLevel = cls.env["product.packaging.level"]
        pack_level_data = [
            ("internal", 3, 1, 0),
            ("retail", 10, 1, 1),
            ("transport", 20, 1, 1),
            ("pallet", 30, 1, 1),
        ]
        required_pack_level_ids = set()
        for name, seq, gtin, req in pack_level_data:
            pack = PackLevel.create(
                {
                    "name": name,
                    "code": name.upper(),
                    "sequence": seq,
                    "has_gtin": gtin,
                }
            )
            if req:
                required_pack_level_ids.add(pack.id)
        cls.required_pack_levels = PackLevel.browse(required_pack_level_ids)

        cls.device = cls.device_obj.create(
            {
                "name": "Test Device",
                "device_type": "zippcube",
                "state": "ready",
                "warehouse_id": 1,
            }
        )

        cls.wizard = cls.cs_wizard.create({"device_id": cls.device.id})

        cls.product_1 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_7")
        cls.products = cls.product_1 | cls.product_2

        cls.product_1.barcode = "424242"
        cls.create_product_packagings()

    @classmethod
    def create_product_packagings(cls):
        # Mimic behavior of product_packaging_type_required, which was
        # creating packaging for packaging levels with required = true
        # can be dropped if we decide we want it back
        for product in cls.products:
            pack_vals = []
            for pack_level in cls.required_pack_levels:
                vals = {
                    "packaging_level_id": pack_level.id,
                    "name": pack_level.name,
                }
                pack_vals.append((0, 0, vals))
            product.packaging_ids = pack_vals

    def _wizard_scan_barcode(self, wizard, barcode):
        wizard.on_barcode_scanned(barcode)
        wizard.onchange_product_id()

    def _wizard_set_product(self, wizard, product):
        with Form(wizard) as wizard_form:
            wizard_form.product_id = product

    def test_product_onchange(self):
        self.assertEqual(len(self.wizard.line_ids), 0)
        self._wizard_set_product(self.wizard, self.product_1)
        self.assertEqual(len(self.wizard.line_ids), 6)

    def test_product_onchange_barcode(self):
        self.assertFalse(self.wizard.product_id)
        self.assertFalse(self.wizard.line_ids)
        self._wizard_scan_barcode(self.wizard, "424242")
        self.assertEqual(self.wizard.product_id, self.product_1)
        self.assertEqual(len(self.wizard.line_ids), 6)

    def setup_wizard(self, verify=True):
        self._wizard_set_product(self.wizard, self.product_1)
        fields = ["packaging_length", "width", "height", "weight", "volume"]
        for idx, line in enumerate(self.wizard.line_ids):
            return_value = TestZippcubeWizard.get_measure_result(
                100 * 2**idx, 100, 100, 3**idx
            )
            line.measuring_select_for_measure()
            self.device._update_packaging_measures(return_value)
            if not verify:
                continue
            self.assertEqual(
                line.read(fields)[0],
                {
                    "id": line.id,
                    "packaging_length": (2**idx) * 1000,
                    "width": 1000,
                    "height": 1000,
                    "weight": 3.0**idx,
                    "volume": 2.0**idx,
                },
            )
        self.wizard.action_save()

    def test_zippcube_measures(self):
        self.setup_wizard()
        mm_uom = self.env.ref("uom.product_uom_millimeter")
        self.assertEqual(
            self.product_1.read(
                [
                    "product_length",
                    "product_width",
                    "product_height",
                    "weight",
                    "volume",
                    "dimensional_uom_id",
                ]
            )[0],
            {
                "id": self.product_1.id,
                "product_length": 1000,
                "product_width": 1000,
                "product_height": 1000,
                "weight": 1.0,
                "volume": 1.0,
                "dimensional_uom_id": (mm_uom.id, mm_uom.name),
            },
        )
        packagings = self.product_1.packaging_ids.sorted()
        self.assertEqual(len(packagings), 5)
        self.assertEqual(set(packagings.mapped("length_uom_name")), {"mm"})
        for idx, packaging in enumerate(packagings, 1):
            self.assertEqual(
                packaging.read(
                    ["packaging_length", "width", "height", "weight", "volume"]
                )[0],
                {
                    "id": packaging.id,
                    "packaging_length": (2**idx) * 1000,
                    "width": 1000,
                    "height": 1000,
                    "weight": 3.0**idx,
                    "volume": 2.0**idx,
                },
            )

    def test_wizard_actions(self):
        self.setup_wizard(verify=False)
        res = self.wizard.action_reopen_fullscreen()
        self.assertEqual(res["res_id"], self.wizard.id)
        res = self.wizard.reload()
        self.assertEqual(res, {"type": "ir.actions.client", "tag": "soft_reload"})
        self.wizard._notify("Test message")
        self.wizard.line_ids[-1].scan_requested = True
        res = self.wizard.action_close()
        self.assertEqual(
            res,
            {
                "type": "ir.actions.act_window",
                "res_model": self.device._name,
                "res_id": self.device.id,
                "view_mode": "form",
                "target": "main",
                "flags": {"headless": False, "clear_breadcrumbs": True},
            },
        )
        test_product = self.product_2
        self.assertNotEqual(self.wizard.product_id, test_product)
        test_product.packaging_ids[1].measuring_device_id = self.device
        res = self.device.open_wizard()
        self.assertEqual(res["context"]["default_product_id"], test_product.id)
        self.wizard.retrieve_product()
        self.assertEqual(self.wizard.product_id, test_product)
        self.assertFalse(self.wizard.line_ids[-1].measuring_select_for_measure())
        self.assertTrue(self.wizard.line_ids[-1].measuring_select_for_measure_cancel())
        self.device.state = "not_ready"
        self.device.test_device()
        self.assertEqual(self.device.state, "ready")
