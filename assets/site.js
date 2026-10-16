(() => {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches

  // 主题切换：记住用户选择；未选择时跟随系统
  const root = document.documentElement
  const themeMeta = document.querySelector('meta[name="theme-color"]')
  const applyTheme = (theme) => {
    root.dataset.theme = theme
    themeMeta.content = theme === 'light' ? '#f1f2f0' : '#252825'
  }
  applyTheme(root.dataset.theme)
  const themeButton = document.querySelector('[data-theme-toggle]')
  themeButton.addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light'
    try { localStorage.setItem('ctxa-theme', next) } catch {}
    if (!document.startViewTransition || reduceMotion) {
      applyTheme(next)
      return
    }
    // 圆心与半径用相对视口的百分比，页面缩放或嵌入式预览时也落在按钮上
    const rect = themeButton.getBoundingClientRect()
    const width = document.documentElement.clientWidth
    const height = innerHeight
    const x = (rect.left + rect.width / 2) / width
    const y = (rect.top + rect.height / 2) / height
    // circle() 的百分比半径以 √(w²+h²)/√2 为 100%
    const radius = (Math.hypot(Math.max(x, 1 - x) * width, Math.max(y, 1 - y) * height) / (Math.hypot(width, height) / Math.SQRT2)) * 100
    const at = `at ${x * 100}% ${y * 100}%`
    const transition = document.startViewTransition(() => applyTheme(next))
    transition.ready.then(() => {
      root.animate(
        { clipPath: [`circle(0% ${at})`, `circle(${radius + 1}% ${at})`] },
        { duration: 650, easing: 'cubic-bezier(0.65, 0, 0.35, 1)', pseudoElement: '::view-transition-new(root)' },
      )
    })
  })
  matchMedia('(prefers-color-scheme: light)').addEventListener('change', (event) => {
    let saved = null
    try { saved = localStorage.getItem('ctxa-theme') } catch {}
    if (!saved) applyTheme(event.matches ? 'light' : 'dark')
  })

  // 首屏手机：循环演示一次闭环，滚出视野或页面隐藏时暂停
  const demo = document.querySelector('[data-demo]')
  const count = demo.querySelector('[data-demo-count]')
  const BASE_COUNT = 127
  const tap = (name) => {
    const target = demo.querySelector(`[data-tap="${name}"]`)
    target.classList.remove('is-tapping')
    void target.offsetWidth
    target.classList.add('is-tapping')
    setTimeout(() => target.classList.remove('is-tapping'), 600)
  }
  const setStage = (stage) => {
    demo.dataset.stage = stage
    const finished = stage === 'done'
    count.textContent = String(BASE_COUNT + (finished ? 1 : 0))
    count.classList.toggle('is-bump', finished)
  }
  // [开始时间 ms, 动作]
  const TIMELINE = [
    [0, () => setStage('front')],
    [1500, () => tap('front')],
    [1800, () => setStage('def')],
    [4300, () => tap('start')],
    [4600, () => setStage('quiz')],
    [6300, () => tap('pick')],
    [6500, () => setStage('answer')],
    [9300, () => setStage('done')],
  ]
  const LOOP = 11800
  let timers = []
  let running = false
  const play = () => {
    if (running) return
    running = true
    const cycle = () => {
      timers = TIMELINE.map(([at, action]) => setTimeout(action, at))
      timers.push(setTimeout(cycle, LOOP))
    }
    cycle()
  }
  const stop = () => {
    running = false
    timers.forEach(clearTimeout)
    timers = []
  }
  if (reduceMotion) {
    setStage('def')
  } else {
    setStage('front')
    let visible = false
    const sync = () => (visible && !document.hidden ? play() : stop())
    new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync() }, { threshold: 0.35 }).observe(demo)
    document.addEventListener('visibilitychange', sync)
  }

  // 后续段落滚动到时淡入
  const revealer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('is-in')
      revealer.unobserve(entry.target)
    })
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' })
  document.querySelectorAll('[data-reveal]').forEach((el) => revealer.observe(el))

  // 顶栏离开首屏后加底色
  const bar = document.querySelector('[data-bar]')
  const updateBar = () => bar.classList.toggle('is-solid', window.scrollY > 24)
  window.addEventListener('scroll', updateBar, { passive: true })
  updateBar()

  // 试一题：作答后显示对错、逐项解析与最强迷惑项
  const quiz = document.querySelector('[data-quiz]')
  const choices = [...quiz.querySelectorAll('[data-choice]')]
  const notes = [...quiz.querySelectorAll('[data-note]')]
  const verdict = quiz.querySelector('[data-verdict]')
  const feedback = quiz.querySelector('[data-feedback]')

  const answer = (picked) => {
    const right = picked.hasAttribute('data-right')
    choices.forEach((choice) => {
      choice.disabled = true
      choice.classList.toggle('is-right', choice.hasAttribute('data-right'))
      choice.classList.toggle('is-wrong', choice === picked && !right)
      choice.classList.toggle('is-dim', choice !== picked && !choice.hasAttribute('data-right'))
    })
    notes.forEach((note) => {
      const key = note.dataset.note
      note.classList.toggle('is-key', key === 'a' || key === picked.dataset.choice)
    })
    verdict.textContent = right ? '答对了。' : '选错了，看看为什么。'
    quiz.classList.add('is-answered')
    setTimeout(() => feedback.scrollIntoView({ block: 'nearest', behavior: 'smooth' }), 420)
  }

  const reset = () => {
    choices.forEach((choice) => {
      choice.disabled = false
      choice.classList.remove('is-right', 'is-wrong', 'is-dim')
    })
    quiz.classList.remove('is-answered')
    choices[0].focus()
  }

  choices.forEach((choice) => choice.addEventListener('click', () => answer(choice)))
  quiz.querySelector('[data-reset]').addEventListener('click', reset)

  // 中文辅助开关
  const assist = quiz.querySelector('[data-assist]')
  const cn = quiz.querySelector('[data-cn]')
  assist.addEventListener('click', () => {
    const on = assist.getAttribute('aria-pressed') !== 'true'
    assist.setAttribute('aria-pressed', String(on))
    cn.hidden = !on
  })

  // 小程序码未放入时，显示品牌标志作为占位
  document.querySelectorAll('[data-qr]').forEach((qr) => {
    const img = qr.querySelector('[data-qr-img]')
    const markMissing = () => {
      qr.classList.add('is-missing')
      const cap = qr.querySelector('[data-qr-cap]')
      if (cap) cap.textContent = '微信小程序 · 语境自修'
    }
    if (img.complete && img.naturalWidth === 0) markMissing()
    img.addEventListener('error', markMissing)
  })

  // 复制小程序名称
  const toast = document.querySelector('[data-toast]')
  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const original = button.textContent
      try {
        await navigator.clipboard.writeText(button.dataset.copy)
        button.textContent = '已复制'
        toast.textContent = '已复制「语境自修」，打开微信搜索即可。'
      } catch {
        toast.textContent = '复制没有成功，请在微信中手动搜索「语境自修」。'
      }
      setTimeout(() => { button.textContent = original }, 1800)
    })
  })
})()
