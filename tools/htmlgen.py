def loginalert(detail):
    html = """
        <div class="alert alert-danger" role="alert"><svg class="icon icon-tabler icon-tabler-alert-triangle" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;font-size: 20px;margin-bottom: 0px;">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M12 9v2m0 4v.01"></path>
            <path d="M5 19h14a2 2 0 0 0 1.84 -2.75l-7.1 -12.25a2 2 0 0 0 -3.5 0l-7.1 12.25a2 2 0 0 0 1.75 2.75"></path>
        </svg><span><strong>Login failed</strong><br />{{ detail }}<br /></span></div>
    """
    html = html.replace("{{ detail }}", detail)
    return html
    
    