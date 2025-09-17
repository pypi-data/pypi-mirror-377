from odoo.addons.component.core import Component
from datetime import datetime

# 5 mins in seconds to delay the jobs
ETA = 300


class ContractLineListener(Component):
    _inherit = "contract.line.listener"

    def on_record_create(self, record, fields=None):
        super().on_record_create(record, fields=fields)
        one_shot_products_categ_id_list = [
            self.env.ref("somconnexio.mobile_oneshot_service").id,
            self.env.ref("somconnexio.broadband_oneshot_service").id,
            self.env.ref("somconnexio.broadband_oneshot_adsl_service").id,
        ]
        service_products_categ_id_list = (
            self.env["service.technology"]
            .search([])
            .mapped("service_product_category_id")
            .ids
        )

        multimedia_service_product_categ_id_list = (
            self._get_multimedia_service_categ_id_list()
        )

        additional_service_products_categ_id_list = [
            self.env.ref("somconnexio.broadband_additional_service").id,
            self.env.ref("somconnexio.mobile_additional_service").id,
        ]

        if record.product_id.categ_id.id in one_shot_products_categ_id_list:
            self.env["contract.contract"].with_delay(eta=ETA).add_one_shot(
                record.contract_id.id, record.product_id.default_code
            )
        elif record.product_id.categ_id.id in (
            service_products_categ_id_list + additional_service_products_categ_id_list
            + multimedia_service_product_categ_id_list
        ):
            self.env["contract.contract"].with_delay(eta=ETA).add_service(
                record.contract_id.id, record
            )

    def on_record_write(self, record, fields=None):
        super().on_record_write(record, fields=fields)
        if record.date_end:
            eta = 0
            if record.date_end > datetime.today().date():
                end_datetime = datetime.combine(record.date_end, datetime.min.time())
                eta = end_datetime - datetime.today()
            self.env["contract.contract"].with_delay(eta=eta).terminate_service(
                record.contract_id.id, record
            )

    def _get_multimedia_service_categ_id_list(self):
        multimedia_service = self.env.ref("multimedia_somconnexio.multimedia_service")
        multimedia_service_childs = self.env["product.category"].search(
            [("parent_id", "=", multimedia_service.id)]
        )
        return multimedia_service_childs.ids
