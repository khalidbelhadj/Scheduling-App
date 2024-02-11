const NUMBER_OF_HOURS = 12;
const CELL_HEIGHT = 100 / NUMBER_OF_HOURS;

const deleteIcon = `<?xml version="1.0" encoding="UTF-8"?><svg width="24px" height="24px" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" color="#000000"><path d="M6.75827 17.2426L12.0009 12M17.2435 6.75736L12.0009 12M12.0009 12L6.75827 6.75736M12.0009 12L17.2435 17.2426" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></svg> `
const editIcon = ` <?xml version="1.0" encoding="UTF-8"?><svg width="24px" height="24px" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg" color="#000000"><path d="M14.3632 5.65156L15.8431 4.17157C16.6242 3.39052 17.8905 3.39052 18.6716 4.17157L20.0858 5.58579C20.8668 6.36683 20.8668 7.63316 20.0858 8.41421L18.6058 9.8942M14.3632 5.65156L4.74749 15.2672C4.41542 15.5993 4.21079 16.0376 4.16947 16.5054L3.92738 19.2459C3.87261 19.8659 4.39148 20.3848 5.0115 20.33L7.75191 20.0879C8.21972 20.0466 8.65806 19.8419 8.99013 19.5099L18.6058 9.8942M14.3632 5.65156L18.6058 9.8942" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></svg> `

const cols = Array.from(document.querySelectorAll('.cal-col'));
cols.forEach(col => (
  Array.from(col.children).filter(child => child.classList.contains('cal-cell'))[0].setAttribute("style", `
  border-top: 0.5px solid #aaa;
  `)
))

function createEventModal(day: number) {
  const modalBackground = document.createElement('div');
  modalBackground.setAttribute("style", `
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background-color: rgba(0, 0, 0, 0.5);
`);
  modalBackground.onclick = () => {
    modal.remove();
    modalBackground.remove();
  }

  const modal = document.createElement('div');
  modal.classList.add('modal');
  modal.setAttribute("style", `
position: fixed;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
background-color: white;
padding: 20px;
box-shadow: 0 0 5px 0 #aaa;
`);
  modal.innerHTML = `
<label for=start-time>Start Time</label>
<input name="start-time" type="time" id="event-start" placeholder="Start Time">
<br>
<label for=end-time>End Time</label>
<input type="time" id="event-end" placeholder="End Time">
<br>
<button id="create-event">Create Event</button>
`;

  document.body.appendChild(modalBackground);
  document.body.appendChild(modal);

  document.getElementById('create-event')!.onclick = () => {
    const startTime = document.getElementById('event-start')!["value"];
    const endTime = document.getElementById('event-end')!["value"];

    let start = +startTime.split(':')[0];
    let end = +endTime.split(':')[0];


    start += +startTime.split(':')[1] / 60;
    end += +endTime.split(':')[1] / 60;

    if (+start < 9 || +end > 20) return alert('Invalid time range. Please select a time between 9 and 18.');
    if (+start >= +end) return alert('Invalid time range. Please select a start time that is less than the end time.');

    createEvent(day, start, end, window["name"]);
    modal.remove();
    modalBackground.remove();
  }
}

function zeroPad(num: number) {
  return num < 10 ? `0${num}` : num;
}

function editEventModal(event, day, start, end) {
  const modalBackground = document.createElement('div');
  modalBackground.setAttribute("style",  `
position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
background-color: rgba(0, 0, 0, 0.5);
`);
  modalBackground.onclick = () => {
    modal.remove();
    modalBackground.remove();
  }
  console.log(start,end)

  const startHour = Math.floor(start + 8);
  const startMin = zeroPad(Math.floor((start + 8 - startHour) * 60));

  const endHour = Math.floor(end + 8);
  const endMin = zeroPad(Math.floor((end + 8 - endHour) * 60));
  const modal = document.createElement('div');
  modal.classList.add('modal');
  modal.setAttribute("style",`
position: fixed;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
background-color: white;
padding: 20px;
box-shadow: 0 0 5px 0 #aaa;
`)
modal.innerHTML = `
<label for=start-time>Start Time</label>
<input name="start-time" type="time" id="event-start" value="${startHour}:${startMin}">
<br>
<label for=end-time>End Time</label>
<input type="time" id="event-end" value="${endHour}:${endMin}">
<br>
<button id="edit-event">Edit Event</button>
`;

  document.body.appendChild(modalBackground);
  document.body.appendChild(modal);

  document.getElementById('edit-event')!.onclick = () => {
    const startTime = document.getElementById('event-start')!["value"];
    const endTime = document.getElementById('event-end')!["value"];

    let start = +startTime.split(':')[0];
    let end = +endTime.split(':')[0];


    start += +startTime.split(':')[1] / 60;
    end += +endTime.split(':')[1] / 60;

    if (+start < 9 || +end > 20) return alert('Invalid time range. Please select a time between 9 and 18.');
    if (+start >= +end) return alert('Invalid time range. Please select a start time that is less than the end time.');

    createEvent(day, start, end, window["name"]);
    modal.remove();
    modalBackground.remove();
    event.remove();
  }
}

function createEvent(day: number, start: number, end: number, text?: string) {
  start = start - 9 + 1;
  end = end - 9 + 1;

  const event = document.createElement('div');
  event.classList.add('event-col');
  event.style.top = `${start * CELL_HEIGHT}%`;
  event.style.height = `${(end - start) * CELL_HEIGHT}%`;

  const child = document.createElement('div');
  child.setAttribute("style", `
display: flex;
justify-content: space-between;
align-items: center;
margin: 5px;
`);
  
  const textDiv = document.createElement('div');
  textDiv.textContent = text || 'Event';
  child.appendChild(textDiv);

  const buttons = document.createElement('div');
  buttons.setAttribute("style", `
display: flex;
justify-content: space-between;
align-items: center;
`)

  const remove = document.createElement('button');
  remove.innerHTML = deleteIcon;
  remove.setAttribute("style", `
background-color: #f1f1f1;
border: none;
border-radius: 5px;
padding: 5px;
display: flex;
height: 20px
width: 20px;
align-items: center;
justify-content: center;
`)
  remove.onclick = () => event.remove()
  buttons.appendChild(remove);

  const edit = document.createElement('button');
  edit.innerHTML = editIcon;

  edit.setAttribute("style", `
background-color: #f1f1f1;
border: none;
border-radius: 5px;
padding: 5px;
display: flex;
height: 30px
width: 30px;
align-items: center;
justify-content: center;
`);
  edit.onclick = () => editEventModal(event, day, start, end);
  buttons.appendChild(edit);

  child.appendChild(buttons);
  event.appendChild(child);

  cols[day].appendChild(event);
}

const days = Array.from(document.querySelectorAll('.day')) as HTMLButtonElement[];

days.forEach((day, idx) => {
  day.onclick = () => createEventModal(idx);
})

createEvent(0, 11, 13, 'Meeting');

console.log("week is", window["week"])

