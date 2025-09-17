from odoo import models

class PartnerMergeLine(models.TransientModel):
    _inherit = 'base.partner.merge.line'

    def merge(self, automatic_merge=True, keep_company=True):
        result = super().merge(automatic_merge=automatic_merge, keep_company=keep_company)

        # Després de la fusió, copia el camp personalitzat
        for line in self:
            if not line.dst_partner_id or not line.src_partner_ids:
                continue

            if not line.dst_partner_id.coopcycle_bind_id:
                for partner in line.src_partner_ids:
                    if partner.coopcycle_bind_id:
                        line.dst_partner_id.coopcycle_bind_id = partner.coopcycle_bind_id
                        break  # només copiem el primer no buit

        return result