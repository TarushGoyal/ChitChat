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

  function add_message(id, sender_name, time, text, reactions, type) {
      // console.log("Adding message : ", type, id, sender_name, time, text, reactions);
      var sender = $('<div class="sender">' + sender_name + '</div>');
      var time = $('<div class="timestamp">' + time + '</div>');
      var message_content;
      if (type == "text")
          message_content = $('<div class="message-content">' + text + '</div>');
      else { // file
          var filename = text.replace(/^.*[\\\/]/, '')
          message_content = $('<div class="message-content"><a href="' + text + '" target="_blank" > <div class="filediv"> 📰️ ' + filename + ' </div> </a></div>');
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
      react_button_tray.append(reply_button);
      var delete_button = $('<button class="delete-button" id="delete-button'+id+'">' + "️🚫️" + '</button>');
      react_button_tray.append(delete_button);
      var complete_message = $('<div class="complete-message"></div>');
      complete_message.append(sender, time, message_content, react_state, react_button_tray, $('<div style="clear:both;"></div>'));
      // if (reply_to) {
      //   complete_message.append($('<p>replied message</p>'))
      // }
      complete_message.mouseenter(() => {react_button_tray.css("display", "inline");});
      complete_message.mouseleave(() => {react_button_tray.css("display", "none");});
      $('.message_holder').append(complete_message);

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
              console.log(chat.type);
              add_message(chat.id, chat.name, chat.posted_at, samaan, {
                 like  : chat.like,
                 love  : chat.love,
                 angry : chat.angry,
                 laugh : chat.laugh,
                 wow   : chat.wow,
                 sad   : chat.sad,
              }, chat.type);
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
        }, "text");
    }
    else if (msg.type == "file"){
      add_message(msg.id, msg.posted_by_name, msg.posted_at, msg.link, {
          like  : 0,
          love  : 0,
          angry : 0,
          laugh : 0,
          wow   : 0,
          sad   : 0,
        }, "file");
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

} );
