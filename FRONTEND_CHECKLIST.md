# Antigravity Frontend - Implementation Checklist

**Project:** Marcus AI Avatar - Frontend Layer  
**Backend:** Separate (FastAPI on port 8000) - DO NOT MIX  
**Timeline:** 6-8 hours MVP, 12-16 hours polished

---

## Pre-Flight Checklist (Before Starting)

- [ ] Backend is running (`http://localhost:8000/health` returns healthy)
- [ ] Docker Desktop is running (for Redis)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] pnpm installed (`pnpm --version`) or use npm

---

## Phase 1: Foundation (2 hours)

### 1.1 Project Initialization
- [x] Create `frontend/` directory at project root
- [x] Run `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
- [x] Verify dev server starts (`cd frontend && npm run dev`)
- [x] Access `http://localhost:3000` - see Next.js welcome page

### 1.2 Dependencies Installation
- [x] Install R3F: `npm install three @react-three/fiber @react-three/drei`
- [x] Install animation: `npm install framer-motion`
- [x] Install utilities: `npm install clsx tailwind-merge`
- [x] Install types: `npm install -D @types/three`
- [x] Verify `package.json` has all dependencies

### 1.3 Configuration Files
- [ ] Create `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Update `frontend/tsconfig.json` (enable strict mode)
- [ ] Update `frontend/tailwind.config.ts` (add custom colors/spacing)
- [ ] Create `frontend/next.config.js` (disable strict mode for R3F)

### 1.4 Directory Structure
- [ ] Create `frontend/src/lib/` directory
- [ ] Create `frontend/src/hooks/` directory
- [ ] Create `frontend/src/types/` directory
- [ ] Create `frontend/src/components/3d/` directory
- [ ] Create `frontend/src/components/ui/` directory
- [ ] Create `frontend/src/components/chat/` directory

### 1.5 API Client Setup
- [ ] Create `frontend/src/lib/api.ts` with fetch wrapper
- [ ] Create `frontend/src/lib/utils.ts` with `cn()` helper
- [ ] Create `frontend/src/types/api.ts` with Message/Chat interfaces
- [ ] Test API connection: Create test page that calls `/health`
- [ ] Verify console shows "Backend status: healthy"

### 1.6 Backend CORS Update (ONLY BACKEND CHANGE)
- [ ] Open `src/config.py` in backend
- [ ] Update `cors_origins_str` to include `http://localhost:3000`
- [ ] Restart backend (`python3 -m uvicorn src.api.main:app --reload`)
- [ ] Verify no CORS errors in frontend browser console

**Phase 1 Complete:** ✅ Frontend talks to backend, no errors

---

## Phase 2: 3D Background (1.5 hours)

### 2.1 Basic Scene Setup
- [ ] Create `frontend/src/components/3d/Scene.tsx` (Canvas wrapper)
- [ ] Add ambient light + point light
- [ ] Test: See blank 3D canvas (no errors in console)

### 2.2 Particle Field
- [ ] Create `frontend/src/components/3d/ParticleField.tsx`
- [ ] Generate 1000 random particle positions (Float32Array)
- [ ] Add `useFrame` hook for slow rotation
- [ ] Test: See white dots floating in space

### 2.3 Portal Effect
- [ ] Create `frontend/src/components/3d/Portal.tsx`
- [ ] Create torus geometry (ring shape)
- [ ] Add MeshStandardMaterial with emissive glow
- [ ] Add rotation animation in `useFrame`
- [ ] Test: See glowing rotating ring

### 2.4 Integration with Layout
- [ ] Open `frontend/src/app/layout.tsx`
- [ ] Add Scene component as fixed background layer
- [ ] Verify 3D renders behind UI content
- [ ] Test: Navigate pages, 3D stays in background

**Phase 2 Complete:** ✅ 3D background renders at 60fps

---

## Phase 3: UI System (2 hours)

### 3.1 Design Tokens
- [ ] Open `frontend/src/app/globals.css`
- [ ] Define CSS custom properties (colors, spacing, shadows)
- [ ] Add `.glass-card` class with backdrop-filter
- [ ] Add `.magnetic-button` base styles
- [ ] Test: Apply classes to dummy elements

### 3.2 Button Component
- [ ] Create `frontend/src/components/ui/Button.tsx`
- [ ] Add prop types: `variant`, `size`, `disabled`
- [ ] Implement Framer Motion wrapper
- [ ] Add magnetic effect hook (`useMagneticButton`)
- [ ] Test: Button pulls towards cursor on hover

### 3.3 GlassCard Component
- [ ] Create `frontend/src/components/ui/GlassCard.tsx`
- [ ] Apply glassmorphism styles
- [ ] Add prop types: `padding`, `blur`, `opacity`
- [ ] Test: Card has frosted glass effect

### 3.4 Input Component
- [ ] Create `frontend/src/components/ui/Input.tsx`
- [ ] Style with focus effects (border glow)
- [ ] Add label animation (float on focus)
- [ ] Test: Input feels fluid, not janky

### 3.5 Component Demo Page (Optional Dev Tool)
- [ ] Create `frontend/src/app/demo/page.tsx`
- [ ] Display all components with examples
- [ ] Test different variants/states
- [ ] Verify responsive on mobile (browser DevTools)

**Phase 3 Complete:** ✅ Reusable UI components ready

---

## Phase 4: Chat Integration (2 hours)

### 4.1 Chat Types
- [ ] Create `frontend/src/types/chat.ts`
- [ ] Define `Message` interface (role, content, timestamp)
- [ ] Define `Conversation` interface (id, messages, etc.)
- [ ] Match backend schema exactly

### 4.2 Chat Hook
- [ ] Create `frontend/src/hooks/useChat.ts`
- [ ] Implement state: `messages`, `isLoading`, `error`
- [ ] Implement `sendMessage()` function
- [ ] Add optimistic updates (user message shows immediately)
- [ ] Add error handling with rollback
- [ ] Test: Log state changes in console

### 4.3 MessageList Component
- [ ] Create `frontend/src/components/chat/MessageList.tsx`
- [ ] Map over messages array
- [ ] Style user vs assistant messages differently
- [ ] Add auto-scroll to bottom (useEffect + ref)
- [ ] Add loading state (three dots animation)
- [ ] Test: Messages stack correctly, scroll works

### 4.4 MessageInput Component
- [ ] Create `frontend/src/components/chat/MessageInput.tsx`
- [ ] Use textarea (not input) for multiline
- [ ] Handle Enter key (send), Shift+Enter (newline)
- [ ] Disable during loading
- [ ] Clear input after send
- [ ] Test: Send message, input clears, loading shows

### 4.5 Chat Page
- [ ] Create `frontend/src/app/chat/page.tsx`
- [ ] Use `useChat` hook
- [ ] Render MessageList + MessageInput
- [ ] Add GlassCard wrapper for chat container
- [ ] Position over 3D background
- [ ] Test: Full flow (type → send → see response)

**Phase 4 Complete:** ✅ Chat works end-to-end with Marcus AI

---

## Phase 5: Polish & Optimization (2-4 hours)

### 5.1 Micro-Interactions
- [ ] Add stagger animation to message list (Framer Motion)
- [ ] Add spring bounce to button clicks
- [ ] Add ripple effect on card hover
- [ ] Add cursor trail (optional, subtle)
- [ ] Test: Every interaction feels "alive"

### 5.2 Loading States
- [ ] Add skeleton loading for messages
- [ ] Add "Marcus is thinking..." indicator
- [ ] Add fade-in for new messages
- [ ] Test: No blank states, always feedback

### 5.3 Error Handling
- [ ] Add toast notifications (sonner library)
- [ ] Show error if backend unreachable
- [ ] Add retry button on failed messages
- [ ] Test: Disconnect backend, verify error UX

### 5.4 Performance Audit
- [ ] Run Lighthouse in Chrome DevTools
- [ ] Check Performance score (target: 90+)
- [ ] Check Accessibility score (target: 95+)
- [ ] Check Best Practices score (target: 95+)
- [ ] Fix any issues flagged

### 5.5 Cross-Browser Testing
- [ ] Test in Chrome (desktop)
- [ ] Test in Safari (desktop + iOS)
- [ ] Test in Firefox
- [ ] Fix any rendering bugs

### 5.6 Mobile Responsiveness
- [ ] Test on iPhone viewport (DevTools)
- [ ] Test on Android viewport (DevTools)
- [ ] Verify touch interactions work
- [ ] Adjust 3D complexity for mobile (fewer particles)

**Phase 5 Complete:** ✅ Production-ready polish

---

## Final Quality Gates (Pre-Launch)

### Code Quality
- [ ] Run ESLint: `npm run lint` (zero errors)
- [ ] Run TypeScript check: `npm run type-check` (zero errors)
- [ ] No `console.log` statements in production code
- [ ] All components have TypeScript prop types
- [ ] No `any` types (search codebase)

### Performance
- [ ] 3D scene runs at 60fps (check DevTools FPS meter)
- [ ] Page load < 3 seconds (Lighthouse)
- [ ] No layout shift (CLS < 0.1)
- [ ] Images use next/image (if any added)

### Accessibility
- [ ] Keyboard navigation works (Tab through UI)
- [ ] Focus indicators visible
- [ ] Color contrast passes WCAG AA
- [ ] Screen reader test (VoiceOver/NVDA)

### Security
- [ ] No API keys in frontend code (search for "sk-")
- [ ] All env vars use `NEXT_PUBLIC_` prefix
- [ ] `.env.local` in `.gitignore`

### Documentation
- [ ] Add README.md in `frontend/` directory
- [ ] Document how to start dev server
- [ ] Document environment variables needed
- [ ] Add screenshots (optional)

---

## Troubleshooting Checklist

### Backend Connection Issues
- [ ] Backend running? (`curl http://localhost:8000/health`)
- [ ] CORS configured? (Check `src/config.py`)
- [ ] Correct API URL in `.env.local`?
- [ ] Browser console shows CORS errors? (Update backend)

### 3D Rendering Issues
- [ ] Check browser console for WebGL errors
- [ ] Try different browser (Safari has WebGL quirks)
- [ ] Reduce particle count (1000 → 500)
- [ ] Disable OrbitControls in production

### TypeScript Errors
- [ ] Run `npm install` (missing types?)
- [ ] Check `tsconfig.json` (strict mode issues?)
- [ ] Add `@ts-expect-error` only as last resort
- [ ] Restart TypeScript server (VS Code: Cmd+Shift+P → Restart TS)

### Performance Issues
- [ ] Check FPS in DevTools (Performance tab)
- [ ] Reduce 3D complexity (fewer particles, simpler shaders)
- [ ] Disable animations in `prefers-reduced-motion`
- [ ] Use production build (`npm run build`)

---

## Success Metrics (Definition of Done)

✅ **MVP Complete:**
- Chat works (send message → receive AI response)
- 3D background renders smoothly
- UI feels premium (glassmorphism, smooth animations)
- No console errors
- Works on desktop Chrome + Safari

✅ **Polish Complete:**
- Lighthouse Performance > 90
- All micro-interactions implemented
- Mobile responsive
- Cross-browser tested
- Error handling implemented

✅ **Production Ready:**
- All quality gates passed
- Documentation complete
- No TypeScript/ESLint errors
- Ready to deploy (Vercel/Netlify)

---

## Notes

**DO:**
- Test frequently (after every component)
- Commit often (small, atomic commits)
- Ask questions when stuck
- Take breaks (avoid burnout)

**DON'T:**
- Mix backend work in this chat
- Skip TypeScript types
- Ignore accessibility
- Over-optimize prematurely

**Estimated Timeline:**
- **Phase 1:** 2 hours
- **Phase 2:** 1.5 hours
- **Phase 3:** 2 hours
- **Phase 4:** 2 hours
- **Phase 5:** 2-4 hours
- **Total:** 9.5-11.5 hours (with breaks: 2 days)

---

**Ready to start?** Begin with Phase 1, Checklist Item 1.1 ✨



