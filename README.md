<p align="center">
  <img alt="reacty Logo" src="https://cdn.labs.brry.cc/file/20d217d8-ca63-4f6e-b2f0-99897ef684ae" width="350px">
</p>
<p align="center">
  <img alt="Deploy status" src="https://github.com/berrysauce/reacty/actions/workflows/deploy.yml/badge.svg">
  <img alt="CodeQL status" src="https://github.com/berrysauce/reacty/actions/workflows/codeql-analysis.yml/badge.svg">
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/berrysauce/reacty">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/berrysauce/reacty">
  <img alt="Website" src="https://img.shields.io/website?down_color=red&down_message=down&up_color=green&up_message=up&url=https%3A%2F%2Freacty.net">
</p>
<p align="center">Finally, a simple and privacy oriented website feedback widget</p>

## What is reacty?
It's a feedback widget you can implement in your site with one line of code. It's responsive, works across platforms, and it doesn't collect user specific data.

## How does it work?
1. Sign up via the website - you don't even need an email address to sign up, just enter your domain and a password
2. Copy and paste the given line of code in your website's `<head></head>` section
3. See the feedback of your users roll in

## Frequently Asked Questions
>Q: Does reacty use cookies?\
>A: No, but reacty uses the browser's local storage to only display the widget once (if the user answered or closed it).

>Q: Why is reacty free?\
>A: It's free because I barely have any costs. reacty is hosted serverlessly and the data is on Deta's NoSQL database.

>Q: How secure is reacty?\
>A: reacty is built with security and privacy in mind. Passwords are hashed, salted, and stored on an encrypted database. Feedback can only be submitted through your website. Still, you should never use the same password for multiple services.

>Q: What kinds of data does reacty collect/store?\
>A: It only stores data like login info and preferences. For feedback collection, reacty only stores the feedback counts.

>Q: Does the widget influence my website's load times?\
>A: Not largely. Speed is a big priority, that's why reacty is optimized for fast loading speeds.

## License
reacty - A simple and privacy oriented website feedback widget.
Copyright (C) 2021 Paul Haedrich (berrysauce)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For any questions or inquiries, contact reacty[at]berrysauce.me.
