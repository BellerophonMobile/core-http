Ext.define('core.store.Nodes', {
    extend: 'Ext.data.Store',
    autoLoad: false,
    autoSync: true,
    model: 'core.model.Node',
    storeId: 'nodeStore',
});
