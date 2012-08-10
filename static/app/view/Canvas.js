Ext.define('core.view.Canvas', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.core.view.Canvas',
    layout: 'fit',
    items: [{
        xtype: 'draw',
        viewBox: false,
        autoScroll: true,
    }],
});
