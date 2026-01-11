/** @odoo-module */

import { registry } from "@web/core/registry";

/**
 * RFID Service
 * Manages WebSocket connection to RFID reader and handles tag detection
 */
export const rfidService = {
    dependencies: ["pos", "notification"],
    
    start(env, { pos, notification }) {
        let websocket = null;
        let isConnecting = false;
        let reconnectTimer = null;
        let listeners = new Set();
        
        const config = {
            url: 'ws://localhost:8765',
            autoConnect: true,
            soundEnabled: true,
            reconnectDelay: 3000,
            maxReconnectAttempts: 5,
            reconnectAttempts: 0,
        };
        
        /**
         * Connect to WebSocket server
         */
        async function connect() {
            if (websocket || isConnecting) {
                console.log('[RFID] Already connected or connecting');
                return;
            }
            
            isConnecting = true;
            
            try {
                console.log(`[RFID] Connecting to ${config.url}...`);
                
                websocket = new WebSocket(config.url);
                
                websocket.onopen = () => {
                    console.log('[RFID] WebSocket connected');
                    isConnecting = false;
                    config.reconnectAttempts = 0;
                    notifyListeners('connected', null);
                    notification.add('RFID Reader connected', {
                        type: 'success',
                        sticky: false,
                    });
                };
                
                websocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('[RFID] Received:', data);
                        
                        // Handle different message types
                        if (data.type === 'welcome') {
                            console.log('[RFID] Server welcome:', data.message);
                            notifyListeners('server_message', data);
                        } else if (data.type === 'tag' || data.type === 'rfid' || data.type === 'scan') {
                            // Handle RFID tag data
                            handleRfidData(data);
                        } else if (data.type === 'error') {
                            console.error('[RFID] Server error:', data.message);
                            notifyListeners('server_error', data);
                        } else if (data.type) {
                            // Other message types, just log
                            console.log('[RFID] Message type:', data.type, data);
                            notifyListeners('server_message', data);
                        } else {
                            // No type field, treat as RFID tag data
                            handleRfidData(data);
                        }
                    } catch (error) {
                        console.error('[RFID] Error parsing message:', error);
                        // Try to handle as plain text RFID tag
                        if (typeof event.data === 'string' && event.data.trim()) {
                            handleRfidData(event.data.trim());
                        }
                    }
                };
                
                websocket.onerror = (error) => {
                    console.error('[RFID] WebSocket error:', error);
                    isConnecting = false;
                };
                
                websocket.onclose = () => {
                    console.log('[RFID] WebSocket closed');
                    websocket = null;
                    isConnecting = false;
                    notifyListeners('disconnected', null);
                    
                    // Attempt to reconnect
                    if (config.reconnectAttempts < config.maxReconnectAttempts) {
                        config.reconnectAttempts++;
                        console.log(`[RFID] Reconnecting in ${config.reconnectDelay}ms (attempt ${config.reconnectAttempts})`);
                        reconnectTimer = setTimeout(() => {
                            connect();
                        }, config.reconnectDelay);
                    } else {
                        notification.add('RFID Reader disconnected. Please check the connection.', {
                            type: 'warning',
                        });
                    }
                };
                
            } catch (error) {
                console.error('[RFID] Connection error:', error);
                isConnecting = false;
                notification.add('Failed to connect to RFID Reader', {
                    type: 'danger',
                });
            }
        }
        
        /**
         * Disconnect from WebSocket server
         */
        function disconnect() {
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
                reconnectTimer = null;
            }
            
            if (websocket) {
                websocket.close();
                websocket = null;
            }
            
            config.reconnectAttempts = config.maxReconnectAttempts; // Prevent reconnect
        }
        
        /**
         * Handle RFID data from WebSocket
         */
        function handleRfidData(data) {
            // Support different data formats
            let rfidTag = null;
            
            if (typeof data === 'string') {
                // Plain string format
                rfidTag = data;
            } else if (data.type === 'tag' || data.type === 'rfid' || data.type === 'scan') {
                // Message with type field
                rfidTag = data.tag || data.rfid || data.id || data.data;
            } else if (data.tag) {
                // { "tag": "RFID-001" }
                rfidTag = data.tag;
            } else if (data.rfid) {
                // { "rfid": "RFID-001" }
                rfidTag = data.rfid;
            } else if (data.id) {
                // { "id": "RFID-001" }
                rfidTag = data.id;
            } else if (data.data) {
                // { "data": "RFID-001" }
                rfidTag = data.data;
            }
            
            if (rfidTag && rfidTag.trim()) {
                rfidTag = rfidTag.trim();
                console.log('[RFID] Tag detected:', rfidTag);
                notifyListeners('tag_read', rfidTag);
                
                // Play sound if enabled
                if (config.soundEnabled) {
                    playBeep();
                }
            } else {
                console.warn('[RFID] Received data but could not extract tag:', data);
            }
        }
        
        /**
         * Play beep sound
         */
        function playBeep() {
            try {
                // Create a simple beep using Web Audio API
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (error) {
                console.error('[RFID] Error playing sound:', error);
            }
        }
        
        /**
         * Add event listener
         */
        function addEventListener(callback) {
            listeners.add(callback);
            return () => listeners.delete(callback);
        }
        
        /**
         * Notify all listeners
         */
        function notifyListeners(event, data) {
            listeners.forEach(callback => {
                try {
                    callback(event, data);
                } catch (error) {
                    console.error('[RFID] Listener error:', error);
                }
            });
        }
        
        /**
         * Get connection status
         */
        function isConnected() {
            return websocket !== null && websocket.readyState === WebSocket.OPEN;
        }
        
        /**
         * Update configuration
         */
        function updateConfig(newConfig) {
            Object.assign(config, newConfig);
        }
        
        /**
         * Load configuration from POS config
         */
        async function loadConfig() {
            try {
                const IrConfigParameter = env.services.orm;
                const params = await IrConfigParameter.call(
                    'ir.config_parameter',
                    'get_param',
                    ['weha_pos_rfid_tag.websocket_url', 'ws://localhost:8765']
                );
                
                if (params) {
                    config.url = params;
                }
            } catch (error) {
                console.error('[RFID] Error loading config:', error);
            }
        }
        
        // Auto-connect if enabled
        loadConfig().then(() => {
            if (config.autoConnect) {
                setTimeout(() => connect(), 1000);
            }
        });
        
        return {
            connect,
            disconnect,
            isConnected,
            addEventListener,
            updateConfig,
            getConfig: () => ({ ...config }),
        };
    },
};

registry.category("services").add("rfid", rfidService);
