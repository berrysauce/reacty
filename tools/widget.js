document.write(`
    <div role="alert" id="reactyWidget" style="border-radius: 10px;border: 1px gray solid;font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,Liberation Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji, sans-serif;opacity: 1;background: rgba(0,0,0,0.85);padding: 10px;position: fixed;bottom: 0;left: 0;margin-left: 20px;margin-right: 20px;margin-bottom: 20px;z-index: 99;opacity: 1;-webkit-transition: opacity 1000ms linear;transition: opacity 1000ms linear;">
        <div role="alert" style="padding: 12px;padding-bottom: 0px;">
            <div style="text-align: center; margin-bottom: 15px;">
                <strong id="widgetTitle" style="color: rgb(255,255,255);font-size: 20px;line-height: 26px;font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,Liberation Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji, sans-serif;max-width: 250px;display: block;">[widgettext]<br /></strong>
                <div style="margin-top: 10px;">
                    <a id="widgetPositive" style="background: rgba(255,255,255,0);font-size: 30px;padding-left: 10px;padding-right: 10px;text-decorations: none;" onclick="returnFeedback(1)">😃</a>
                    <a id="widgetNeutral" style="background: rgba(255,255,255,0);font-size: 30px;padding-left: 10px;padding-right: 10px;text-decorations: none;" onclick="returnFeedback(2)">😐</a>
                    <a id="widgetNegative" style="background: rgba(255,255,255,0);font-size: 30px;padding-left: 10px;padding-right: 10px;text-decorations: none;" onclick="returnFeedback(3)">🙁</a>
                </div>
            </div>
            <p style="margin-bottom: 6px;color: rgb(130,130,130);font-size: 12px;margin-top: 10px;font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,Liberation Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji, sans-serif;">powered by <a style="text-decoration: underline; color: rgb(130,130,130);" href="https://reacty.net?ref=widget" target="_blank">reacty</a>
                <button type="button" style="font-size: 12px;padding: 0px;background: rgba(0,0,0,0);border-style: none;font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,Liberation Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji, sans-serif; color: rgba(255,255,255); float: right;" onclick="closeWidget()">Close</button>
            </p>
        </div>
    </div>

    <script>
        function closeWidget() {
            const widget = document.getElementById("reactyWidget")
            widget.style.opacity = '0';
            setTimeout(function(){widget.style.visibility = "hidden";}, 1000);
        }
        function returnFeedback(feedback) {
            let url = "https://reacty.net/api/[webkey]/report/" + feedback
            fetch(url)

            document.getElementById("widgetPositive").style.visibility = "hidden";
            document.getElementById("widgetNeutral").style.visibility = "hidden";
            document.getElementById("widgetNegative").style.visibility = "hidden";
            document.getElementById("widgetTitle").innerHTML = "Thank you!";

            closeWidget()
        }
    </script>
`)