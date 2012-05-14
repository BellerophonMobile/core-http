Ext.define('core.view.Canvas', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.canvas',
    layout: 'fit',
    items: [{
        xtype: 'draw',
        viewBox: false,
        autoScroll: true,
    }],
});
