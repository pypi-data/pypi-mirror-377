/* Javascript for SlackXBlock. */
function SlackXBlock(runtime, element) {
  function updateCount(result) {
    $(".count", element).text(result.count);
  }

  var handlerUrl = runtime.handlerUrl(element, "increment_count");

  $("p", element).click(function (eventObject) {
    $.ajax({
      type: "POST",
      url: handlerUrl,
      data: JSON.stringify({ hello: "world" }),
      success: updateCount,
    });
  });

  $(function ($) {
    /* Here's where you'd do things on page load. */
  });
}

function SlackXBlock(runtime, element) {
  var $element = $(element);

  // Handle join channel click
  $element.find(".join-channel-btn").on("click", function (e) {
    var channelName = $(this).data("channel");

    // Call the XBlock handler
    $.ajax({
      type: "POST",
      url: runtime.handlerUrl(element, "join_channel"),
      data: JSON.stringify({ channel: channelName }),
      success: function (result) {
        console.log("Successfully tracked channel join");
      },
    });

    // Let the link work normally (open in new tab)
    return true;
  });

  // Load channel info on page load
  $.ajax({
    type: "POST",
    url: runtime.handlerUrl(element, "get_channel_info"),
    data: JSON.stringify({}),
    success: function (result) {
      if (result.workspace_configured) {
        console.log(
          "Slack workspace configured for channel:",
          result.channel_name
        );
      }
    },
  });
}
