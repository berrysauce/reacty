document.write(`
    <div role="alert" id="feeedWidget" style="border-radius: 10px;border-style: none;font-family: Inter, sans-serif;opacity: 1;background: rgba(0,0,0,0.85);padding: 10px;position: fixed;bottom: 0;left: 0;margin-left: 20px;margin-right: 20px;margin-bottom: 20px;opacity: 1;-webkit-transition: opacity 500ms linear;transition: opacity 500ms linear;">
    <div role="alert" style="padding: 12px;padding-bottom: 0px;">
        <div style="text-align: center; margin-bottom: 15px;">
            <strong style="color: rgb(255,255,255);font-size: 20px;line-height: 26px;font-family: Inter, sans-serif;">What do you think?<br /></strong>
            <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 10px" onclick="returnFeedback(1)">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-mood-happy" style="font-size: 35px;color: rgb(74,217,24);">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <circle cx="12" cy="12" r="9"></circle>
                    <line x1="9" y1="9" x2="9.01" y2="9"></line>
                    <line x1="15" y1="9" x2="15.01" y2="9"></line>
                    <path d="M8 13a4 4 0 1 0 8 0m0 0h-8"></path>
                </svg>
            </button>
            <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 10px" onclick="returnFeedback(2)">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-mood-neutral" style="font-size: 35px;color: rgb(224,228,34);">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <circle cx="12" cy="12" r="9"></circle>
                    <line x1="9" y1="10" x2="9.01" y2="10"></line>
                    <line x1="15" y1="10" x2="15.01" y2="10"></line>
                    <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
            </button>
            <button type="button" class="reaction" style="background: rgba(255,255,255,0);border-style: none;font-size: 35px;margin-top: 10px" onclick="returnFeedback(3)">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icon-tabler-mood-sad" style="font-size: 34px;color: rgb(231,38,38);">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <circle cx="12" cy="12" r="9"></circle>
                    <line x1="9" y1="10" x2="9.01" y2="10"></line>
                    <line x1="15" y1="10" x2="15.01" y2="10"></line>
                    <path d="M9.5 15.25a3.5 3.5 0 0 1 5 0"></path>
                </svg>
            </button>
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