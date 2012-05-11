Ext.define('core.view.Canvas', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.canvas',
    layout: 'fit',
    items: [{
        xtype: 'draw',
        viewBox: false,
        autoScroll: true,
            autoRender: true,
            autoShow: true,
        //autoSize: true,
        //items: [{
        //    type: 'circle',
        //    fill: '#79BB3F',
        //    radius: 100,
        //    x: 150,
        //    y: 150,
        //}],
    }],
});
