// availability.js
// Handles toggling timeslot availability via AJAX (POST to /sysadmin/availability/toggle/)

function getCSRFToken() {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.switch').forEach(function (input) {
    input.addEventListener('change', function (e) {
      const slotId = e.target.getAttribute('data-slot-id');
      if (!slotId) return;

      const formData = new FormData();
      formData.append('slot_id', slotId);

      fetch('/sysadmin/availability/toggle/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
        },
        body: formData,
        credentials: 'same-origin'
      }).then(res => res.json()).then(data => {
        // Update UI based on response
        const slotEl = document.querySelector(`.slot[data-slot-id="${data.id}"]`);
        if (!slotEl) return;
        const badge = slotEl.querySelector('.badge');
        const checkbox = slotEl.querySelector('.switch');
        if (data.available) {
          badge.classList.remove('red');
          badge.textContent = 'Available';
          slotEl.classList.remove('disabled');
          checkbox.checked = true;
        } else {
          badge.classList.add('red');
          badge.textContent = 'Not Available';
          slotEl.classList.add('disabled');
          checkbox.checked = false;
        }
      }).catch(err => {
        console.error('Toggle error', err);
        // revert checkbox UI state
        e.target.checked = !e.target.checked;
      });
    });
  });
});
