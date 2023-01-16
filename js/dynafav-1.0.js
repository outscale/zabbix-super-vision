//
// DynaFav for Outscale Monitoring
//
// This is a dynamic favicon implementation for monitoring dashboards.
//
// Copyright 2020 Outscale SAS
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is furnished
// to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
// FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.
//

document.addEventListener("DOMContentLoaded", () => {

	// Get the Head tag.
	var head = document.getElementsByTagName('head')[0];

	// Remove possible existing favicon link
	var link = document.querySelector("link[rel~=icon]");
	if (link)
		link.parentElement.removeChild(link);

	// Create the Favicon item
	var el = document.createElement('link');
	el.type = 'image/x-icon';
	el.rel = 'icon';

	// Create the Canvas to draw the icon.
	var canvas = document.createElement('canvas');

	if (!canvas.getContext)
	  return;

	var ctx = canvas.getContext('2d');

	// No need to size too big, browser will size down.
	canvas.height = canvas.width = 16; // set the size

	var centerX = canvas.width / 2;
	var centerY = canvas.height / 2;
	var radius = centerX;

	// Count the events we got, check if we got disasters ?
	var events = document.querySelectorAll("table.alerts > tbody > tr").length
	var disasters = document.querySelectorAll("table.alerts > tbody > tr.disaster").length

	// Create the icon background with adequate icon/color
	var symbol = '√';
	ctx.fillStyle = 'green';
	if (disasters > 0) {
		ctx.fillStyle = 'red';
		symbol = '!';
	} else if (events > 0) {
		ctx.fillStyle = 'orange';
		symbol = '~';
	}


	// Draw the circle with fill color
	ctx.beginPath();
	ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
	ctx.fill();

	// Draw the symbol
	ctx.fillStyle = "white";
	ctx.textAlign = "center";
	ctx.font = 'bold 12px "helvetica", sans-serif';
	ctx.fillText(symbol, centerX, centerY + centerY / 2);

	// Event count
	ctx.textAlign = "end";
	ctx.font = '11px "courier", monospace';
	// - Hard Shadow
	ctx.fillStyle = "rgba(255,255,255,0.7)";
	ctx.fillText(events, canvas.width - 2, canvas.height - 2);
	ctx.fillText(events, canvas.width - 2, canvas.height);
	ctx.fillText(events, canvas.width, canvas.height - 2);
	ctx.fillText(events, canvas.width, canvas.height);
	// - Actual count
	ctx.fillStyle = 'black';
	ctx.fillOpacity = 1;
	ctx.fillText(events, canvas.width - 1, canvas.height - 1);

	// Set link to data-href.
	el.href = canvas.toDataURL('image/png');

	// Add the link to page head.
	head.appendChild(el);

	return;

});

