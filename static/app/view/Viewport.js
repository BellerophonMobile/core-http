Ext.define('core.view.Viewport', {
    extend: 'Ext.container.Viewport',
    requires: [
        'core.view.Canvas',
        'core.view.Palette',
    ],
    layout: 'border',
    items: [{
        xtype: 'core.view.Canvas',
        region: 'center',
    }, {
        xtype: 'core.view.Palette',
        region: 'west',
        collapsible: true,
        split: true,
    }],
});
