window.addEventListener('DOMContentLoaded', (event) => {

    document.addEventListener('click', (event) => {
        const target = event.target;

        // if post edit/save button is clicked
        if (target.classList.contains('post-btn')) {
            // initialize button, post, post_id and content element divs of onclicked post container
			let button = target;
            let post = button.parentElement.parentElement;
            let content_element = post.querySelector('.post-content');
            let post_id = post.querySelector('input[name="post_id"]').value;

            // if edit is requested, replace content with textarea, filled with previous content
            if (button.innerHTML == 'Edit') {
                // create textarea and replace with p tag
                let content = content_element.innerHTML;

                let textarea = document.createElement('textarea');
                textarea.classList.add('form-control', 'm-2', 'post-content');
                textarea.innerHTML = content;

                content_element.replaceWith(textarea);
                // change button label
                button.innerHTML = 'Save';

            } 
            else if (button.innerHTML == 'Save') {
                // if save is requested, POST new content
                let csrf = post.querySelector('input[name="csrfmiddlewaretoken"]').value;
                let content = content_element.value;
                fetch('/edit', {
                    method: 'POST',
                    body: JSON.stringify({
                        post_id:post_id,
                        new_content:content
                    }),
                    headers: {'X-CSRFToken':csrf}
                })    
                .then(response => {
                    // if bad request, append error message container
                    if (response.status == 400) {
                        // create and append error message div
                        let message = document.createElement('div')
                        message.classList.add('alert', 'alert-danger', 'm-2');
                        message.innerHTML = "Content must not be empty";

                        post.append(message);
                    }
                    else {
                      // in case of success, finish proccess, create p 
                      // element with new content and replace it with textarea
                      let p = document.createElement('p');
                      p.classList.add('post-content');
                      p.innerHTML = content;
      
                      content_element.replaceWith(p);

                      // change button label
                      button.innerHTML = 'Edit';

                      // remove error message if it is displayed
                      let error_message = post.querySelector('.alert');
                      if (error_message) {
                          error_message.remove();
                      }
                    }
                });
            }
        }

        // elif post like/unlike icon is clicked
        else if (target.classList.contains('likeicon')) {
            let post = target.parentElement.parentElement.parentElement;
            let post_id = post.querySelector('input[name="post_id"]').value;
            let csrf = post.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch('/like', {
                method: 'PUT',
                body: JSON.stringify({
                    post_id:post_id,
                }),
                headers: {'X-CSRFToken':csrf}
            })    
            .then(response => {
                // if bad request, append error message container
                if (response.status == 302) {
                    // redirect if not logged in
                    window.location.href = "/login";
                }
                else {
                    if (target.classList.contains('fa-heart')) {
                        // change like icon
                        target.classList.remove('fa-heart')
                        target.classList.add('fa-heart-o');

                        // decrement counter by 1
                        let counter = post.querySelector('.like-counter');
                        let num = parseInt(counter.innerHTML);
                        counter.innerHTML = num - 1;
                    }
                    else {
                        // change like icon
                        target.classList.remove('fa-heart-o');
                        target.classList.add('fa-heart')

                        // decrement counter by 1
                        let counter = post.querySelector('.like-counter');
                        let num = parseInt(counter.innerHTML);
                        counter.innerHTML = num + 1;
                    }
                }
            });
        }

        // elif follow/unfollow button is clicked
        else if (target.id == 'followbtn') {
            let csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            let profile_id = target.parentElement.querySelector('input[name="profile_pk"]').value;

            fetch('/follow', {
                method: 'PUT',
                body: JSON.stringify({
                    profile_id:profile_id,
                }),
                headers: {'X-CSRFToken':csrf}
            })    
            .then(response => {
                // if bad request, append error message container
                if (response.status == 302) {
                    // redirect if not logged in
                    window.location.href = "/login";
                }
                else {
                    let counter = document.querySelector('#follower-count');
                    let num = parseInt(counter.innerHTML);

                    // if operation was follow
                    if (target.innerHTML.trim() == 'Follow') {
                        // change label
                        target.innerHTML = 'Unfollow';

                        // increment followers counter by 1
                        counter.innerHTML = num + 1;
                    }
                    // elif operation was unfollow
                    else if (target.innerHTML.trim() == 'Unfollow') {
                        // change label
                        target.innerHTML = 'Follow';

                        // decrement followers counter by 1
                        counter.innerHTML = num - 1;
                    }
                }
            });
        }
    });
});