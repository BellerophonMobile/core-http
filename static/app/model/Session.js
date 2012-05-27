Ext.define('core.model.Session', {
    extend: 'Ext.data.Model',
    fields: ['id', 'name', 'user'],

    hasMany: {model: 'core.model.Node', name: 'nodes'},

    proxy: {
        type: 'rest',
        url: '/sessions/',
        reader: {
            type: 'json',
        },
        writer: {
            type: 'json',
        },
    },
});
