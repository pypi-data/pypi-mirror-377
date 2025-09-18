from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ErrorNotImplemented(Exception):
    pass


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    is_multimedia = fields.Boolean(
        compute="_compute_is_multimedia",
        store=True,
    )

    @api.depends("product_id")
    def _compute_is_multimedia(self):
        service_multimedia = self.env.ref(
            "multimedia_somconnexio.multimedia_service", raise_if_not_found=False
        )
        if not service_multimedia:
            # If the main multimedia service is not found,
            # set all lines to not multimedia
            for record in self:
                record.is_multimedia = False
            return
        for record in self:
            record.is_multimedia = (
                service_multimedia.id == record.product_id.categ_id.parent_id.id
            )

    def create_multimedia_contract(self):
        """
        Create a multimedia contract from a lead line
        """

        if not self.is_multimedia:
            raise ValidationError(_("This lead line is not a multimedia service."))

        supplier_id = self._get_service_supplier()
        contract_vals = self._prepare_contract_vals_from_line(supplier_id)
        contract = self.env["contract.contract"].create(contract_vals)

        return contract

    def _get_service_supplier(self):
        """
        Get the service supplier for the multimedia contract.
        This needs to overridden in subclasses to provide specific suppliers.
        :return: Service supplier record (or raise an error if not implemented).
        """
        raise ErrorNotImplemented()
