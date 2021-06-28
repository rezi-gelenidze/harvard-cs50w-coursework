document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#mail-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  // Clear out composition fields and hide error message if it was displayed before
  document.querySelector('#compose-message').style.display = 'none';
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Handle form submition (sending email)
  let form = document.querySelector('#compose-form');
  form.onsubmit = function() {
    // get form data
    let recipients = document.querySelector('#compose-recipients').value;
    let subject = document.querySelector('#compose-subject').value;
    let body = document.querySelector('#compose-body').value;

    // POST data
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: recipients,
          subject: subject,
          body: body
      })
    })
    .then(response => response.json())
    .then(result => {
        // if error, show error message container
        if (result.error) {
          let messagebox = document.querySelector('#compose-message');
          messagebox.style.display = 'block';
          messagebox.innerHTML = result.error;
        }
        else {
          // in case of success, load mailbox of sent mails
          load_mailbox('sent');
        }
    });
  
    return false;
  } 
}


function load_mailbox(mailbox) {
  let mailbox_view = document.querySelector('#emails-view');
  
  // Show the mailbox and hide other views
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'none';
  mailbox_view.style.display = 'block';

  // Show the mailbox name
  mailbox_view.innerHTML = `<h3 class="page-title">${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // fetch results and render
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {

    if (emails.length == 0) {
      let emptymessage = document.createElement('h5')
      emptymessage.innerHTML = 'Empty.';
      emptymessage.classList.add('font-weight-bold');
      mailbox_view.append(emptymessage);
    }

    let usermail;
    if (mailbox.toLowerCase() == 'sent') {
      usermail = 'recipients';
    }
    else {
      usermail = 'sender';
    }

    let newMail;
    let archivebtn;
    let innertext;
    let rowelement;

    emails.forEach(mail => {
      if (mailbox == 'inbox' || mailbox == 'archive') {
        // create and add classes
        archivebtn = document.createElement('button');
        archivebtn.classList.add('btn', 'btn-outline-dark', 'btn-sm', 'ml-5');
        
        // fill with label
        innertext = 'Archive';
        if (mailbox == 'archive') {
          innertext = 'Unarchive';
        }

        archivebtn.innerHTML = innertext;
        archivebtn.addEventListener('click', (event) => {
          // prevent parent event call
          event.stopPropagation();

          // change archived state of mail
          fetch(`/emails/${mail.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                archived: !mail.archived
            })
          })

          // start hiding animation and remove row
          rowelement = event.target.parentElement;
          rowelement.style.animationPlayState = 'running';
          rowelement.addEventListener('animationend', () => {
            rowelement.remove();
            if (mailbox == 'archive') {
              load_mailbox('inbox');
            }
          })
        });
      }

      // create new mail div
      newMail = document.createElement('div');
      newMail.classList.add('mailrow');
      newMail.innerHTML = `
        <span class='usermail'>${mail[usermail]}</span>
        <span class='subject'>${mail.subject}</span>
        <span class='date'>${mail.timestamp}</span>
      `;
      if (archivebtn) {
        newMail.append(archivebtn);
      }
      
      if (mail.read == true) {
        newMail.style.backgroundColor = '#bdc7c9';
      }

      mailbox_view.append(newMail);
      newMail.addEventListener('click', () => view_mail(mail.id));
    })
  })
}


function view_mail(mail_id) {
  // Show mail view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'block';

  // fetch mail data
  fetch(`/emails/${mail_id}`)
  .then(response => response.json())
  .then(email => {
    // fill email div template with data
    document.querySelector('#from').innerHTML = `<b>From:</b> ${email.sender}`;
    document.querySelector('#to').innerHTML = `<b>To:</b> ${email.recipients}`;
    document.querySelector('#subject').innerHTML = `<b>Subject:</b> ${email.subject}`;
    document.querySelector('#timestamp').innerHTML = `<b>timestamp:</b> ${email.timestamp}`;
    document.querySelector('#mail-body').innerHTML = email.body;

    // add reply button listener
    document.querySelector('#replybtn').onclick = () => {
      // open compose mail page
      compose_email();
      let subject_field = document.querySelector('#compose-subject');
      let body_field = document.querySelector('#compose-body');
      let recipients_field = document.querySelector('#compose-recipients');

      // fill recipients field
      recipients_field.value = email.sender;

      // determine subject field content
      if (email.subject.substring(0,3) != 'Re:') {
        subject_field.value = 'Re: ' + email.subject;
      }
      else {
        subject_field.value = email.subject;
      }

      // fill body field
      body_field.value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
    }

    // mark email as read if it is not already marked
    if (email.read == false) {
      fetch(`/emails/${mail_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      });
    }
  });
}