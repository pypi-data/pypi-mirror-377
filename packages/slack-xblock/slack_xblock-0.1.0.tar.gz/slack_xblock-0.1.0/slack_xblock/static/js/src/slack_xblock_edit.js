function SlackLinkXBlockStudio(runtime, element) {
  $(element)
    .find(".save-button")
    .on("click", function () {
      var handlerUrl = runtime.handlerUrl(element, "submit_edits");
      var data = {
        slack_channel_url: $(element).find("#slack-link-xblock-url").val(),
        button_text: $(element).find("#slack-link-xblock-button-text").val(),
        description_text: $(element)
          .find("#slack-link-xblock-description-text")
          .val(),
        display_name: $(element).find("#slack-link-xblock-display-name").val(),
      };
      runtime.post(handlerUrl, JSON.stringify(data)).done(function (response) {
        // Handle response, e.g., show a success message or refresh the editor
        // For now, we'll just log and assume success
        console.log("XBlock settings saved:", response);
        runtime.notify("save", { state: "saved" }); // Notify Studio that changes were saved
      });
    });

  $(element)
    .find(".cancel-button")
    .on("click", function () {
      runtime.notify("cancel", {}); // Notify Studio that the user canceled
    });
}
