$(function () {

  $('textarea.mention').mentionsInput({
    onDataRequest:function (mode, query, callback) {
      var data = [
        { id:1, name:'Hồ Đông Tú', 'avatar':'', 'type':'user' },
        { id:2, name:'Nguyễn Quang Phú', 'avatar':'', 'type':'user' },
        { id:3, name:'Bùi Nhật Dương', 'avatar':'', 'type':'user' },
        { id:4, name:'Nguyễn Trần Phương Linh', 'avatar':'', 'type':'user' },
        { id:5, name:'Hoàng Thế Nam', 'avatar':'', 'type':'user' },
        { id:6, name:'Nguyễn Huy Toàn', 'avatar':'', 'type':'user' },
        { id:7, name:'Nguyễn Mai Hương', 'avatar':'', 'type':'user' },
        { id:8, name:'Vũ Thị Huyền Anh', 'avatar':'', 'type':'user' },
        { id:9, name:'Lê Tuấn Tú', 'avatar':'', 'type':'user' },
        { id:11, name:'Dữ Liệu', 'avatar':'', 'type':'category' },
        { id:12, name:'Nhân sự', 'avatar':'', 'type':'category' },
        { id:13, name:'Training Coaching', 'avatar':'', 'type':'category' },
        { id:14, name:'Vận hành', 'avatar':'', 'type':'category' },
        { id:15, name:'Hỗ trợ', 'avatar':'', 'type':'category' },
        { id:16, name:'Giải đáp thắc mắc', 'avatar':'', 'type':'category' },
        { id:17, name:'AAAA', 'avatar':'', 'type':'category' },
        { id:18, name:'09:00', 'avatar':'', 'type':'time' },
        { id:19, name:'09:30', 'avatar':'', 'type':'time' },
        { id:20, name:'10:00', 'avatar':'', 'type':'time' },
        { id:21, name:'10:30', 'avatar':'', 'type':'time' },
        { id:22, name:'11:00', 'avatar':'', 'type':'time' },
        { id:23, name:'11:30', 'avatar':'', 'type':'time' },
        { id:24, name:'12:00', 'avatar':'', 'type':'time' },
        { id:25, name:'12:30', 'avatar':'', 'type':'time' },
        { id:26, name:'13:00', 'avatar':'', 'type':'time' },
        { id:27, name:'13:30', 'avatar':'', 'type':'time' },
        { id:28, name:'14:00', 'avatar':'', 'type':'time' },
        { id:29, name:'New', 'avatar':'', 'type':'action' },
        { id:30, name:'Update', 'avatar':'', 'type':'action' },
        { id:31, name:'Edit', 'avatar':'', 'type':'action' },
        { id:32, name:'Delete', 'avatar':'', 'type':'action' },
      ];

      data = _.filter(data, function(item) { return item.name.toLowerCase().indexOf(query.toLowerCase()) > -1 });

      callback.call(this, data);
    },
	onCaret: true
  });

  $('.get-syntax-text').click(function() {
    $('textarea.mention').mentionsInput('val', function(text) {
      alert(text.split("@").slice(1,text.split("@").length));
      $("#infor_data").val(text.split("@").slice(1,text.split("@").length))
      // alert($("#infor_data").val())
    });
  });

  $('.get-mentions').click(function() {
    $('textarea.mention').mentionsInput('getMentions', function(data) {
      alert(JSON.stringify(data));
      $("#infor_data").val(JSON.stringify(data));
      // alert($("#infor_data").val());
    });
  }) ;

});