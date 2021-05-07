REACT2EMOJI = {
  like : "👍️",
  love : "💟",
  angry : "😡",
  laugh : "😂",
  wow : "😮",
  sad : "😢"
};

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on( 'connect', function() {

  function get_reply_holder(id){
    var reply_sender = $('#complete-message-'+id).find('.sender').first().text();
    var reply_content = $('#complete-message-'+id).find('.message-content').last().text();
    var reply_time = $('#complete-message-'+id).find('.timestamp').first().text();
    return $('<div class="reply-holder"> \
              <div class="sender">' + reply_sender + '</div> \
              <div class="timestamp">' + reply_time + '</div> \
              <div class="message-content">' + reply_content + '</div> \
              </div>');
  }

  function onReacted(id, key) {
      return function() {
          socket.emit('reacted', {
              channel : channel_id,
              message_id : id,
              type : key
          });
      };
  }

  function onDeleted(id) {
      return function() {
          socket.emit('deleted', {
              channel : channel_id,
              message_id : id,
          });
      };
  }

  function onReplied(id) {
      return function() {
        var curr = $('.text-form .reply_id').val();
        if (curr != "" && curr != undefined){
              $('.form-holder .reply-holder').remove();
        }
        if (curr != id){
            $('.form-holder').prepend(get_reply_holder(id));
            $('.text-form .reply_id').val(id);
        }
        else{
            $('.text-form .reply_id').val(undefined);
        }
    };
  }

  function add_message(id, sender_name, time, text, reactions, type, deleted, replied) {
      // console.log("Adding message : ", type, id, sender_name, time, text, reactions);
      var sender = $('<div class="sender">' + sender_name + '</div>');
      var time = $('<div class="timestamp">' + time + '</div>');
      var message_content;
      if (deleted == 1)
          message_content = $('<div class="message-content"> <i>This message has been deleted </i> </div>');
      else if (type == "text")
          message_content = $('<div class="message-content">' + text + '</div>');
      else { // file
          var filename = text.replace(/^.*[\\\/]/, '')
          message_content = $('<div class="message-content"><a href="' + text + '" target="_blank" > <div class="filediv"> 📰️ ' + filename + ' </div> </a></div>');
      }
      var reply_holder;
      if (replied) {
          reply_holder =  get_reply_holder(replied);
      }
      var react_state = $('<div class="react-state"></div>');
      for(var key in REACT2EMOJI) {
          var emoji = REACT2EMOJI[key];
          var react_type = $('<div class="react-type" id="react-type|' + id + '|' + key + '">' + emoji + '</div>');
          var react_num = $('<div class="react-num" id="react-num|'+ id + '|' + key + '">' + reactions[key] + '</div>');
          if (reactions[key] == 0) {
            react_type.hide();
            react_num.hide();
          }
          react_state.append(react_type);
          react_state.append(react_num);
      }
      var react_button_tray = $('<div class="react-button-tray"></div>');
      for (var key in REACT2EMOJI) {
          var emoji =  REACT2EMOJI[key];
          var bt = $('<button class="react-button" id="react-button|'+ id + '|' + key +'">' + emoji + '</button>');
          bt.click(onReacted(id,key));
          react_button_tray.append(bt);
      }

      var reply_button = $('<button class="reply-button" id="reply-button'+id+'">' + "💬️" + '</button>');
      reply_button.click(onReplied(id));
      react_button_tray.append(reply_button);

      var delete_button = $('<button class="delete-button" id="delete-button'+id+'">' + "️🚫️" + '</button>');
      delete_button.click(onDeleted(id));
      react_button_tray.append(delete_button);

      var complete_message = $('<div id="complete-message-' + id + '" class="complete-message"></div>');
      if (deleted)
          complete_message.append(sender, time, message_content);
      else if (replied)
          complete_message.append(sender, time, reply_holder, message_content, react_state, react_button_tray, $('<div style="clear:both;"></div>'));
      else
          complete_message.append(sender, time, message_content, react_state, react_button_tray, $('<div style="clear:both;"></div>'));
      complete_message.mouseenter(() => {react_button_tray.css("display", "inline");});
      complete_message.mouseleave(() => {react_button_tray.css("display", "none");});
      // $('.message_holder').remove($('#message-spacer'));
      $('.message_holder').append(complete_message);
      // $('.message_holder').append($('#message-spacer'));

  }

  function load_chats(keyword, sender) {
    const myNode = document.getElementsByClassName("message_holder")[0];
    myNode.innerHTML = '';
    $.ajax({
        url: '/chats/' + channel_id,
        data : {'keyword' : keyword, 'sender' : sender},
        type: 'POST',
        success: function(response) {
            console.log("Fetched older chats");
            console.log(response);
            msg = response;
            for (var i = 0; i < msg.chats.length; i++) {
              var chat = msg.chats[i];
              var samaan = (chat.type == "text") ? chat.content : chat.link;
              add_message(chat.id, chat.name, chat.posted_at, samaan, {
                 like  : chat.like,
                 love  : chat.love,
                 angry : chat.angry,
                 laugh : chat.laugh,
                 wow   : chat.wow,
                 sad   : chat.sad,
              }, chat.type, chat.deleted,chat.reply_to);
            }
            document.querySelector('.rightcolumn').scrollTop = document.querySelector('.rightcolumn').scrollHeight;
        },
        error: function(error) {
            console.log("Could not fetch chats!",error);
        },
        // processData: false,
        // contentType: false,
        // cache : false
    });
  }

  socket.emit('joined', {
    channel : channel_id
  });

  var form = $( '.text-form' ).on( 'submit', function( e ) {
    e.preventDefault();
    let reply_id = $( 'input.reply_id' ).val();
    let user_input = $( 'input.message' ).val();
    $('.form-holder .reply-holder').remove();
    socket.emit( 'send chat', {
      message : user_input,
      channel : channel_id,
      reply_id : reply_id
    } );
    $( 'input.reply_id' ).val(undefined);
    console.log("Message sent from frontend");
    $( 'input.message' ).val( '' ).focus();
  } );

  var form2 = $( '.file-form' ).on( 'submit', function( e ) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: '/upload',
            data: formData,
            type: 'POST',
            success: function(response) {
                console.log("Uploaded!!!!!!!!!!!!");
                console.log(response);
                socket.emit( 'upload', {
                    'filename' : document.querySelector('input.file').files[0].name,
                    'folder' : response.folder,
                    'channel' : channel_id
                });
                document.querySelector('input.file').value = "";
                console.log("File sent from frontend");
                $( 'input.message' ).val( '' ).focus();
            },
            error: function(error) {
                console.log("Failed!!!!!!!!!!!!!!!",error);
            },
            cache: false,
            contentType: false,
            processData: false
        });
  });

  var form3 = $( '.search-form' ).on( 'submit', function( e ) {
    e.preventDefault();
    // var formData = new FormData(this);
    let keyword = $('.search-form #keyword').val();
    let sender = $('.search-form #sender').val();
    load_chats(keyword = keyword, sender = sender);
  });

  $('#switch-text-button').click(() => {
      load_chats('','');
  });
  $('#switch-file-button').click(() => {
      load_chats('','');
  });


  react_buttons = document.getElementsByClassName('react-button');
  for (var i=0;i<react_buttons.length;i++) {
    var react_button = react_buttons[i];
    react_button.onclick = function() {
      socket.emit('reacted', {
          channel : channel_id,
          message_id : this.id.split('|')[1],
          type : this.id.split('|')[2]
      } )
    }
  }

socket.on('status', function(msg) {
    console.log("received chats!");
    load_chats(keyword = "", sender = "");
});

socket.on('add chat',function(msg) {
    console.log("Socket received : ", msg);
    if (msg.type == "text") {
      add_message(msg.id, msg.posted_by_name, msg.posted_at, msg.content, {
          like  : 0,
          love  : 0,
          angry : 0,
          laugh : 0,
          wow   : 0,
          sad   : 0,
        }, "text", msg.deleted, msg.reply_to);
    }
    else if (msg.type == "file"){
      add_message(msg.id, msg.posted_by_name, msg.posted_at, msg.link, {
          like  : 0,
          love  : 0,
          angry : 0,
          laugh : 0,
          wow   : 0,
          sad   : 0,
        }, "file", msg.deleted, msg.reply_to);
    }
    else {
      console.log("Fucked up! " + msg.type);
    }
    document.querySelector('.rightcolumn').scrollTop = document.querySelector('.rightcolumn').scrollHeight;
})
socket.on('add react',function(msg) {
    // console.log(msg);
    var react_num = document.getElementById("react-num|" + msg.message_id + "|" + msg.type);
    var react_type = document.getElementById("react-type|" + msg.message_id + "|" + msg.type);
    react_num.innerText = parseInt(react_num.innerText) + 1;
    if (react_num.innerText == 1){
        react_num.style.display = "inline";
        react_type.style.display = "inline";
    }
})

socket.on('delete chat',function(msg) {
    $('#complete-message-'+msg.message_id).find('.react-button-tray').remove();
    $('#complete-message-'+msg.message_id).find('.react-state').remove();
    $('#complete-message-'+msg.message_id).find('.reply-holder').remove();
    $('#complete-message-'+msg.message_id).find('.message-content').html('<i>This message has been deleted </i>');
})

} );
