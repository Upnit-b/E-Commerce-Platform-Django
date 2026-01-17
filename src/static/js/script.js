// Vanilla JavaScript - No jQuery dependency

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {

  // Prevent closing from click inside dropdown
  document.addEventListener('click', function (e) {
    if (e.target.closest('.dropdown-menu')) {
      e.stopPropagation()
    }
  })

  // Handle radio button changes
  document.querySelectorAll('.js-check :radio').forEach(function (radio) {
    radio.addEventListener('change', function () {
      const checkAttrName = this.getAttribute('name')
      if (this.checked) {
        // Remove active class from all radios with same name
        document.querySelectorAll('input[name="' + checkAttrName + '"]').forEach(function (input) {
          input.closest('.js-check')?.classList.remove('active')
        })
        // Add active class to checked radio
        this.closest('.js-check')?.classList.add('active')
      }
    })
  })

  // Handle checkbox changes
  document.querySelectorAll('.js-check :checkbox').forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
      if (this.checked) {
        this.closest('.js-check')?.classList.add('active')
      } else {
        this.closest('.js-check')?.classList.remove('active')
      }
    })
  })

  // Initialize Bootstrap tooltips (Bootstrap 5 syntax)
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  if (tooltipTriggerList.length > 0) {
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
  }

  // Auto-hide alert messages after 4 seconds
  const alertMessages = document.querySelectorAll('.alert')
  alertMessages.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    }, 4000)
  })
})
