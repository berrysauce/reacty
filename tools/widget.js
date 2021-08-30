document.write(`
    <div role="alert" id="feeedWidget" style="border-radius: 10px;border-style: none;font-family: Inter, sans-serif;opacity: 1;background: rgba(0,0,0,0.85);padding: 10px;position: fixed;bottom: 0;left: 0;margin-left: 20px;margin-right: 20px;margin-bottom: 20px;opacity: 1;-webkit-transition: opacity 500ms linear;transition: opacity 500ms linear;">
        <div role="alert" style="padding: 12px;padding-bottom: 0px;">
            <div style="text-align: center; margin-bottom: 15px;">
                <strong style="color: rgb(255,255,255);font-size: 20px;line-height: 26px;font-family: Inter, sans-serif;">What do you think?<br /></strong>
                <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 15px" onclick="returnFeedback(1)">😃</button>
                <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 15px" onclick="returnFeedback(2)">😐</button>
                <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 15px" onclick="returnFeedback(3)">🙁</button>
            </div>
            <p style="margin-bottom: 6px;color: rgb(130,130,130);font-size: 12px;margin-top: 9px;font-family: Inter, sans-serif;">powered by <a style="text-decoration: underline; color: rgb(130,130,130);" href="https://usefeeed.com?ref=widget" target="_blank">feeed</a>
                <button type="button" style="font-size: 12px;padding: 0px;background: rgba(0,0,0,0);border-style: none;font-family: Inter, sans-serif; color: rgba(255,255,255); float: right;" onclick="closeWidget()">Close</button>
            </p>
        </div>
    </div>

    <script>
        function closeWidget() {
            const widget = document.getElementById("feeedWidget")
            widget.style.opacity = '0';
            setTimeout(function(){widget.style.visibility = "hidden";}, 500);
        }
        function returnFeedback(feedback) {
            let url = "https://feeed-testing.deta.dev/api/[webkey]/report/" + feedback
            fetch(url)
            closeWidget()
        }
    </script>
`)