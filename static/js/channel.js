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

  function onReacted(id, key) {
      return function() {
          socket.emit('reacted', {
              channel : channel_id,
              message_id : id,
              type : key
          });
      };
  }

  function add_message(id, sender_name, time, text, reactions, reply_to) {
      console.log(id, sender_name, time, text, reactions, reply_to);
      var sender = $('<div class="sender">' + sender_name + '</div>');
      var time = $('<div class="timestamp">' + time + '</div>');
      var message_content = $('<div class="message-content">' + text + '</div>');
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
      react_button_tray.append(reply_button);
      var delete_button = $('<button class="delete-button" id="delete-button'+id+'">' + "️🚫️" + '</button>');
      react_button_tray.append(delete_button);
      var complete_message = $('<div class="complete-message"></div>');
      complete_message.append(sender, time, message_content, react_state, react_button_tray, $('<div style="clear:both;"></div>'));
      if (reply_to) {
        complete_message.append($('<p>replied message</p>'))
      }
      complete_message.mouseenter(() => {react_button_tray.css("display", "inline");});
      complete_message.mouseleave(() => {react_button_tray.css("display", "none");});
      $('.message_holder').append(complete_message);

  }



  socket.emit('joined', {
    channel : channel_id
  });

  var form = $( '.text-form' ).on( 'submit', function( e ) {
    e.preventDefault();
    let user_input = $( 'input.message' ).val();
    socket.emit( 'send chat', {
      message : user_input,
      channel : channel_id
    } );
    console.log("Message sent from frontend");
    $( 'input.message' ).val( '' ).focus();
  } );

  var form2 = $( '.file-form' ).on( 'submit', function( e ) {
    e.preventDefault();
    var file = document.querySelector('input.file').files[0]; //Files[0] = 1st file
    var reader = new FileReader();
    reader.readAsText(file, 'UTF-8');
    reader.onload = (event) => {
      socket.emit( 'upload', {
        'filename' : document.querySelector('input.file').files[0].name,
        'data' : event.target.result,
        'channel' : channel_id
      } );
      document.querySelector('input.file').value = "";
      console.log("File sent from frontend");
      $( 'input.message' ).val( '' ).focus();
    }
  } );

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
    for (var i =0 ;i<msg.chats.length;i++) {
      var chat = msg.chats[i];
      add_message(chat.id, chat.name, chat.posted_at, chat.content, {
         like  : chat.like,
         love  : chat.love,
         angry : chat.angry,
         laugh : chat.laugh,
         wow   : chat.wow,
         sad   : chat.sad,
      });
    }
    document.querySelector('.rightcolumn').scrollTop = document.querySelector('.rightcolumn').scrollHeight;
});

socket.on('add chat',function(msg) {
    console.log(msg);
    add_message(msg.id, msg.posted_by_name, msg.posted_at, msg.content, {
        like  : 0,
        love  : 0,
        angry : 0,
        laugh : 0,
        wow   : 0,
        sad   : 0,
    });
    document.querySelector('.rightcolumn').scrollTop = document.querySelector('.rightcolumn').scrollHeight;
})
socket.on('add react',function(msg) {
    console.log(msg);
    var react_num = document.getElementById("react-num|" + msg.message_id + "|" + msg.type);
    var react_type = document.getElementById("react-type|" + msg.message_id + "|" + msg.type);
    react_num.innerText = parseInt(react_num.innerText) + 1;
    if (react_num.innerText == 1){
        react_num.style.display = "inline";
        react_type.style.display = "inline";
    }
})

} );
