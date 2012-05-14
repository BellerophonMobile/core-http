Ext.define('core.controller.Canvas', {
    extend: 'Ext.app.Controller',
    views: [
        'Canvas',
    ],
    refs: [{
        selector: '.canvas > .draw',
        ref: 'draw',
    }],

    init: function() {
        this.callParent(arguments);
        console.log('Canvas controller init!');
        this.control({
            '.canvas > .draw': {
                click: this.canvasClick,
            }
        });
    },

    canvasClick: function(e, t) {
        var draw = this.getDraw();
        var box = draw.getBox();
        draw.surface.add({
            type: 'circle',
            fill: '#ff0000',
            radius: 100,
            x: e.getX() - box.x,
            y: e.getY() - box.y,
        }).show(true);
    },
});
