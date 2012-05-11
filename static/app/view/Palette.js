Ext.define('core.view.Palette', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.palette',
    title: 'Tools Palette',
    header: false,
    /* Width depends on content, but height does not. */
    shrinkWrap: 1,
    layout: {
        type: 'accordion',
    },
    items: [{
        title: 'Panel 1',
        html: 'Panel 1 content',
    }, {
        title: 'Panel 2',
        html: 'Panel 2 content',
    }],
});
