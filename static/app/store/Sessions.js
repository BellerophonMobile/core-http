Ext.define('core.store.Sessions', {
    extend: 'Ext.data.Store',
    fields: ['id', 'name'],
    data: [
        {id: 0, name: 'test'},
        {id: 1, name: 'foobar'},
    ],
});
