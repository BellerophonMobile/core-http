Ext.define('core.view.Viewport', {
    extend: 'Ext.container.Viewport',
    layout: 'border',
    requires: [
        'core.view.Canvas',
        'core.view.Palette',
    ],
    items: [{
        xtype: 'canvas',
        region: 'center',
    }, {
        xtype: 'palette',
        region: 'west',
        collapsible: true,
        split: true,
    }],
});
