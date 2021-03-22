REACT_MAP = {
  yes : "👍️",
  no : "👎"
};

function update_message(id, react_id) {
  var button_id = msg.message_id * 2 + ((msg.type == "yes") ? 0 : 1);
  var bt = document.getElementById("num" + button_id);
  bt.innerText = parseInt(bt.innerText) + 1;
}

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
      var counter = 0;
      var base_react_id = Object.keys(reactions).length * id;
      for(var key in REACT_MAP) {
          var react_id = base_react_id + counter;
          var emoji = REACT_MAP[key];
          react_state.append('<div class="react-type" id="react-type' + react_id + '">' + emoji + '</div>');
          react_state.append('<div class="react-num" id="react-num'+react_id+'">'+reactions[key]+'</div>');
          counter += 1;
      }
      var react_button_tray = $('<div class="react-button-tray"></div>');
      counter = 0;
      for (var key in REACT_MAP) {
        var react_id = base_react_id + counter;
        var emoji =  REACT_MAP[key];
        var bt = $('<button class="react-button" id="react-button'+react_id+'">' + emoji + '</button>');
        bt.click(onReacted(id,key));
        react_button_tray.append(bt);
        counter += 1;
      }
      var reply_button = $('<button class="reply-button" id="reply-button'+id+'">' + "💬️" + '</button>');
      react_button_tray.append(reply_button);
      var delete_button = $('<button class="delete-button" id="delete-button'+id+'">' + "️🚫️" + '</button>');
      react_button_tray.append(delete_button);
      var complete_message = $('<div class="complete-message"></div>');
      complete_message.append(sender, time, message_content, react_state, react_button_tray);
      if (reply_to) {
        complete_message.append($('<p>replied message</p>'))
      }
      $('.message_holder').append(complete_message);

  }



  socket.emit('joined', {
    channel : channel_id
  });

  var form = $( 'form' ).on( 'submit', function( e ) {
    e.preventDefault();
    let user_input = $( 'input.message' ).val();
    socket.emit( 'send chat', {
      message : user_input,
      channel : channel_id
    } );
    $( 'input.message' ).val( '' ).focus();
  } );

  react_buttons = document.getElementsByClassName('react-button');
  for (var i=0;i<react_buttons.length;i++) {
    var react_button = react_buttons[i];
    react_button.onclick = function() {
      socket.emit('reacted', {
          channel : channel_id,
          message_id : Math.floor(this.id.substr(12)/2),
          type : (this.id.substr(12)%2 == 0) ? "yes" : "no",
      } )
    }
  }

socket.on('status', function(msg) {
    console.log(msg.chats[0]);
    for (var i =0 ;i<msg.chats.length;i++) {
      var chat = msg.chats[i];
      add_message(chat.id, chat.name, chat.posted_at, chat.content, {yes : chat.yes, no: chat.no});
    }
});

socket.on('add chat',function(msg) {
    console.log(msg);
    if( typeof msg.user_name !== 'undefined' ) {
      $( 'h3' ).remove()
      add_message(msg.id, msg.user_name, msg.posted_at, msg.message, {yes : 0, no : 0});
      // $( 'div.message_holder' ).append( '<div><b style="color: #000">'+msg.user_name+'</b> '+msg.message+'</div>' )
    }
})
socket.on('add react',function(msg) {
    console.log(msg);
    var react_id = msg.message_id * 2 + ((msg.type == "yes") ? 0 : 1);
    console.log(react_id);
    var bt = document.getElementById("react-num" + react_id);
    bt.innerText = parseInt(bt.innerText) + 1;
})

} );
