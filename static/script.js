document.addEventListener("DOMContentLoaded", () => {

  //Pomodoro timer 
  const display    = document.getElementById("timer-display");
  const startBtn   = document.getElementById("start-btn");
  const stopBtn    = document.getElementById("stop-btn");
  const form       = document.getElementById("pomodoro-form");
  const studyInput      = document.getElementById("study-input");
  const shortBreakInput = document.getElementById("short-break-input");
  const longBreakInput  = document.getElementById("long-break-input");

  let countdown, secondsLeft;
  let sessionCount = 0;
  let isWork       = true;

  function formatTime(s) {
    const m   = String(Math.floor(s/60)).padStart(2, "0");
    const sec = String(s % 60).padStart(2, "0");
    return `${m}:${sec}`;
  }

  function tick() {
    if (secondsLeft <= 0) {
      clearInterval(countdown);
      if (isWork) {
        sessionCount++;
        isWork = false;
        // Pick break length
        const sb = parseInt(shortBreakInput.value, 10);
        const lb = parseInt(longBreakInput.value, 10);
        const chosenBreak = (sessionCount % 4 === 0) ? lb : sb;
        secondsLeft = chosenBreak * 60;
        display.textContent = formatTime(secondsLeft);
        startCountdown();
      } else {
        display.textContent = "00:00";
        form.submit();
      }
    } else {
      secondsLeft--;
      display.textContent = formatTime(secondsLeft);
    }
  }

  function startCountdown() {
    countdown = setInterval(tick, 1000);
  }

  startBtn.addEventListener("click", () => {
    // Validate study time
    const studyMin = parseInt(studyInput.value, 10);
    if (isNaN(studyMin) || studyMin < 21) { // Makes sure input is a valid number
      return alert("Study time must be at least 21 minutes.");
    }
    // Validate breaks
    const sb = parseInt(shortBreakInput.value, 10);
    const lb = parseInt(longBreakInput.value, 10);
    if ([sb, lb].some(x => isNaN(x) || x < 0 || x > 25)) {
      return alert("Breaks must be between 0 and 25 minutes.");
    }

    startBtn.disabled = true;
    stopBtn.disabled  = false;
    isWork       = true;
    secondsLeft  = studyMin * 60;
    display.textContent = formatTime(secondsLeft);
    // keep the hidden duration in sync so the server logs the study length
    document.getElementById("duration-input").value = studyMin;
    startCountdown();
  });

  stopBtn.addEventListener("click", () => {
    clearInterval(countdown);
    startBtn.disabled = false;
    stopBtn.disabled  = true;
    
    // compute elapsed minutes
    const elapsedMs = Date.now() - startTimestamp;
    const elapsedMin = Math.round(elapsedMs / 60000);

    // set the hidden field & submit
    document.getElementById("duration-input").value = elapsedMin;
    form.submit();




    
  });




 
// Scroll buttons
  document.documentElement.style.scrollBehavior = "smooth";
  document.querySelectorAll(".scroll-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.target;
      document.getElementById(target)?.scrollIntoView();
    });
  });












 // Show/Hide for adding assingment
  document.getElementById("show-assignment-form").addEventListener("click", () => {
    document.getElementById("assign-form").style.display = "block";
  });
  document.getElementById("cancel-assignment").addEventListener("click", () => {
    document.getElementById("assign-form").style.display = "none";
  });

  // ── Add Course Toggle ──
  document.getElementById("show-course-form").addEventListener("click", () => {
    document.getElementById("course-form").style.display = "block";
  });
  document.getElementById("cancel-course").addEventListener("click", () => {
    document.getElementById("course-form").style.display = "none";
  });


  

  // Show/Hide for editing assingment
  
  // Show the inline edit form
  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      document.getElementById(`edit-row-${id}`).style.display = "table-row";
    });
  });

  // Hide the form on cancel
  document.querySelectorAll(".cancel-edit").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      document.getElementById(`edit-row-${id}`).style.display = "none";
    });
  });

  // Habit logger pop up for numeric habit type
  const select = document.getElementById("habit-select");
  const valueLabel = document.getElementById("value-label");

  if (!select || !valueLabel) {
    console.warn("Habit select or value label not found");
    return;
  }

  function updateValueField() {
    const opt = select.selectedOptions[0];
    if (!opt) {
      return valueLabel.style.display = "none";
    }
    valueLabel.style.display = (opt.dataset.type === "numeric")
                              ? "inline-block"
                              : "none";
  }

  select.addEventListener("change", updateValueField);
  updateValueField();  // init on page load


});


// Invisibilty toggle for sidebar
document.addEventListener('DOMContentLoaded', () => {
  window.addEventListener('scroll', () => {
    const sidebar = document.querySelector('.sidebar');
    const homeSection = document.getElementById('home');

    if (!sidebar || !homeSection) return;

    const homeBottom = homeSection.getBoundingClientRect().bottom;

    if (homeBottom < window.innerHeight * 0.1) {
      sidebar.classList.add('visible');
    } else {
      sidebar.classList.remove('visible');
    }
  });
});

