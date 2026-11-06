(() => {
  const shell = document.querySelector('[data-demo-shell]')
  const demo = shell.querySelector('[data-demo]')
  const buttons = [...shell.querySelectorAll('[data-demo-step]')]
  const playback = shell.querySelector('[data-demo-play]')
  const caption = shell.querySelector('[data-demo-caption]')
  const motionPreference = matchMedia('(prefers-reduced-motion: reduce)')
  // Same eleven-segment arc used in the client's Today page.
  const arc = shell.querySelector('[data-goal-arc]')
  for (let index = 0; index < 11; index++) {
    const angle = (-110 + index * 22) * Math.PI / 180
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
    for (const [key, value] of Object.entries({
      x1: 120 + Math.sin(angle) * 91,
      y1: 117 - Math.cos(angle) * 91,
      x2: 120 + Math.sin(angle) * 103,
      y2: 117 - Math.cos(angle) * 103,
    })) line.setAttribute(key, String(value))
    if (index < 7) line.classList.add('is-lit')
    line.style.setProperty('--tick-delay', `${index * 60}ms`)
    arc.append(line)
  }
  const confetti = shell.querySelector('[data-demo-confetti]')
  for (let index = 0; index < 18; index++) {
    const particle = document.createElement('i')
    particle.style.setProperty('--x', `${3 + index * 37 % 94}%`)
    particle.style.setProperty('--turn', `${index % 2 ? 480 : -420}deg`)
    particle.style.setProperty('--particle-delay', `${index % 6 * 90}ms`)
    confetti.append(particle)
  }
  // Scene boundaries are absolute milliseconds; offscreen time never advances the story.
  const timeline = [
    [0, 'front'], [1400, 'tap'], [1900, 'reading'],
    [6500, 'question'], [9600, 'answer'], [12000, 'explanation'],
    [17300, 'completion'], [21600, 'switch'], [22300, 'today'],
  ]
  const chapterAt = { reading: 1900, explanation: 12000, completion: 17300, today: 22300 }
  const loopDuration = 28000
  let position = motionPreference.matches ? 1900 : 0
  let nextEvent = motionPreference.matches ? 3 : 0
  let startedAt = 0
  let timer = null
  let visible = false
  let paused = motionPreference.matches
  const setScene = (scene) => {
    demo.dataset.scene = scene
    const chapter = ['front', 'tap', 'reading'].includes(scene) ? 'reading'
      : ['question', 'answer', 'explanation'].includes(scene) ? 'explanation'
        : ['switch', 'today'].includes(scene) ? 'today' : 'completion'
    for (const button of buttons) {
      const active = button.dataset.demoStep === chapter
      button.setAttribute('aria-pressed', String(active))
      if (active) caption.textContent = button.dataset.caption
    }
    shell.querySelector('[data-demo-count]').textContent = ['completion', 'switch', 'today'].includes(scene) ? '128' : '127'
    shell.querySelector('[data-secondary-icon]').dataset.view = ['explanation', 'completion'].includes(scene) ? 'task' : 'book'
    demo.dataset.chapter = chapter
  }
  const stop = () => {
    demo.dataset.playing = 'false'
    if (timer === null) return
    position += performance.now() - startedAt
    clearTimeout(timer)
    timer = null
  }
  const tick = () => {
    let time = position + performance.now() - startedAt
    if (time >= loopDuration) {
      position = time % loopDuration
      startedAt = performance.now()
      time = position
      nextEvent = 0
    }
    while (nextEvent < timeline.length && time >= timeline[nextEvent][0]) {
      setScene(timeline[nextEvent++][1])
    }
    timer = setTimeout(tick, Math.max(16, (timeline[nextEvent]?.[0] ?? loopDuration) - time))
  }
  const sync = () => {
    if (paused || !visible || document.hidden) return stop()
    demo.dataset.playing = 'true'
    if (timer !== null) return
    startedAt = performance.now()
    tick()
  }
  const updatePlayback = () => {
    playback.textContent = paused ? '播放' : '暂停'
    playback.setAttribute('aria-label', paused ? '播放演示' : '暂停演示')
  }
  for (const button of buttons) {
    button.addEventListener('click', () => {
      stop()
      paused = true
      const scene = button.dataset.demoStep
      position = chapterAt[scene]
      nextEvent = timeline.findIndex(([at]) => at === position) + 1
      setScene(scene)
      updatePlayback()
    })
  }
  playback.addEventListener('click', () => {
    paused = !paused
    updatePlayback()
    sync()
  })
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting
    sync()
  }, { threshold: 0.35 }).observe(demo)
  document.addEventListener('visibilitychange', sync)
  motionPreference.addEventListener('change', (event) => {
    if (!event.matches) return
    stop()
    paused = true
    updatePlayback()
  })
  setScene(motionPreference.matches ? 'reading' : 'front')
  updatePlayback()
})()
