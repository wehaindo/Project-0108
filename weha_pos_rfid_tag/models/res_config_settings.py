# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pos_rfid_websocket_url = fields.Char(
        string='RFID Websocket URL',
        default='ws://localhost:8765',
        config_parameter='weha_pos_rfid_tag.websocket_url',
        help='Websocket server URL for RFID reader (e.g., ws://localhost:8765)'
    )
    
    pos_rfid_auto_connect = fields.Boolean(
        string='Auto Connect to RFID Reader',
        default=True,
        config_parameter='weha_pos_rfid_tag.auto_connect',
        help='Automatically connect to RFID reader when POS opens'
    )
    
    pos_rfid_sound_enabled = fields.Boolean(
        string='Enable Sound on Tag Read',
        default=True,
        config_parameter='weha_pos_rfid_tag.sound_enabled',
        help='Play sound when RFID tag is successfully read'
    )
