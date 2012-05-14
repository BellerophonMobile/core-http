Ext.define('core.view.Palette', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.palette',
    title: 'Tools Palette',
    header: false,
    layout: {
        type: 'vbox',
        align: 'stretch',
        manageOverflow: 2,
    },
    width: 150,
    defaults: {
        xtype: 'buttongroup',
        columns: 4,
        defaults: {
            scale: 'large',
            enableToggle: true,
            toggleGroup: 'palette',
            width: 32,
            height: 32,
        },
    },
    items: [{
        xtype: 'panel',
        layout: 'hbox',
        items: [{
            xtype: 'combobox',
            emptyText: 'Select a session',
            store: 'Sessions',
            queryMode: 'local',
            displayField: 'name',
            valueField: 'id',
            editable: false,
            width: 125,
            height: null,
        }, {
            xtype: 'button',
            tooltip: 'New Session',
            width: 24,
            height: 24,
            componentCls: 'palette palette-new-session',
            enableToggle: false,
            toggleGroup: null,
        }],
    }, {
        xtype: 'button',
        text: 'Start Experiment',
        scale: 'large',
        icon: '/static/resources/images/start.png',
    }, {
        title: 'Tools',
        items: [{
            tooltip: 'Select',
            componentCls: 'palette palette-select',
        }, {
            tooltip: 'Link',
            componentCls: 'palette palette-link',
        }],
    }, {
        title: 'Virtual Nodes',
        items: [{
            tooltip: 'Router',
            componentCls: 'palette palette-router',
        }, {
            tooltip: 'Host',
            componentCls: 'palette palette-host',
        }, {
            tooltip: 'PC',
            componentCls: 'palette palette-pc',
        }, {
            tooltip: 'MDR',
            componentCls: 'palette palette-mdr',
        }, {
            tooltip: 'PRouter',
            componentCls: 'palette palette-prouter',
        }],
    }, {
        title: 'Link-layer Nodes',
        items: [{
            tooltip: 'Ethernet Hub',
            componentCls: 'palette palette-hub',
        }, {
            tooltip: 'Ethernet Switch',
            componentCls: 'palette palette-switch',
        }, {
            tooltip: 'Wireless LAN',
            componentCls: 'palette palette-wlan',
        }, {
            tooltip: 'RJ45 Pysical Interface',
            componentCls: 'palette palette-rj45',
        }, {
            tooltip: 'Tunnel',
            componentCls: 'palette palette-tunnel',
        }],
    }],
});
