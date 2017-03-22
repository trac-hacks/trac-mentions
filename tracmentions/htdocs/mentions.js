jQuery(function ($) {
  $('[data-trac-mentions = all]').mentionsInput({
    elastic: false,
    onDataRequest: function (mode, query, callback) {
      var data = UserList;
      data = _.filter(data, function (item) {
        return item.name.toLowerCase().indexOf(query.toLowerCase()) > -1
      });

      callback.call(this, data);
    },
    resetInput: false
  });
});
