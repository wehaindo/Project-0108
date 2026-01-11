# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _


class OperatingUnitType(models.Model):
    """Operating Unit Types for Hierarchy (HO, DC, Store)"""
    _name = 'operating.unit.type'
    _description = 'Operating Unit Type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Type Name',
        required=True,
        translate=True,
        help='Type of operating unit (e.g., Head Office, Distribution Center, Store)'
    )
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code for this type (e.g., HO, DC, STORE)'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in hierarchy (lower = higher level)'
    )
    level = fields.Integer(
        string='Hierarchy Level',
        required=True,
        default=0,
        help='0=Top Level (HO), 1=Middle (DC), 2=Bottom (Store)'
    )
    can_have_parent = fields.Boolean(
        string='Can Have Parent',
        default=True,
        help='Whether this type can have a parent operating unit'
    )
    can_have_children = fields.Boolean(
        string='Can Have Children',
        default=True,
        help='Whether this type can have child operating units'
    )
    default_revenue_share = fields.Float(
        string='Default Revenue Share (%)',
        default=0.0,
        help='Default percentage of revenue sharing for this level'
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color for visual identification'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Operating unit type code must be unique!'),
    ]
