Ext.define('core.store.Sessions', {
    extend: 'Ext.data.Store',
    autoLoad: true,
    model: 'core.model.Session',
    storeId: 'sessionStore',
});
