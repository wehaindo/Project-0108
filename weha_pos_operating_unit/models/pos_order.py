# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        related='session_id.operating_unit_id',
        store=True,
        readonly=True,
        index=True,
        help='Operating unit from POS session.'
    )
    
    def _create_invoice(self, move_vals):
        """Override to assign operating unit to invoice"""
        # Add operating unit to invoice values (OCA module handles the field)
        if self.operating_unit_id:
            move_vals['operating_unit_id'] = self.operating_unit_id.id
        
        return super()._create_invoice(move_vals)
    
    def _create_misc_reversal_move(self, payment_moves):
        """Override to assign operating unit to reversal entry"""
        # Store operating unit before calling super
        operating_unit_id = self.operating_unit_id.id if self.operating_unit_id else False
        
        result = super()._create_misc_reversal_move(payment_moves)
        
        # Find the reversal entry that was just created and assign operating unit
        if operating_unit_id:
            reversal_entry = self.env['account.move'].search([
                ('ref', 'like', f'Reversal of POS closing entry%{self.name}%')
            ], limit=1, order='id desc')
            
            if reversal_entry:
                reversal_entry.write({'operating_unit_id': operating_unit_id})
        
        return result


class PosPayment(models.Model):
    _inherit = 'pos.payment'
    
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        related='pos_order_id.operating_unit_id',
        store=True,
        readonly=True,
        help='Operating unit from POS order.'
    )
    
    # def _create_payment_moves(self, is_reverse=False):
    #     """Override to assign operating unit to payment moves"""
    #     moves = super()._create_payment_moves(is_reverse=is_reverse)
        
    #     # Assign operating unit to payment moves (OCA module handles line items)
    #     if self.operating_unit_id:
    #         moves.write({'operating_unit_id': self.operating_unit_id.id})
        
    #     return moves

