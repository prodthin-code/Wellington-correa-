import React from 'react';
import { createRoot } from 'react-dom/client';
import MaskedHeading from './components/MaskedHeading/MaskedHeading';
import Lightning from './components/Lightning/Lightning';
import ColorBends from './components/ColorBends/ColorBends';

function mountMaskedHeading() {
  const container = document.getElementById('lab-heading-root');
  if (!container) return;

  const originalContent = container.innerHTML;

  try {
    container.innerHTML = '';
    const root = createRoot(container);
    root.render(
      <MaskedHeading
        text="Modelos simples. Percepções diferentes."
        tag="h2"
        id="lb"
        align="left"
        mediaType="image"
        src="assets/lab-sofisticada.webp"
        reveal="rise"
        trigger="view"
        duration={1.0}
        stagger={0.07}
        spotlight={true}
        spotlightRadius={160}
        fillScale={1.2}
        parallax={16}
        drift={6}
        hoverZoom={0.015}
        brightness={0.85}
        saturation={0.9}
        grayscale={false}
        outline={false}
        serifWords={[2, 3]}
        lineBreakIndices={[1]}
        textScale={0}
        className="lab-masked-h2"
      />
    );
  } catch (err) {
    console.warn('[THIN] Falha ao inicializar MaskedHeading, preservando título original:', err);
    container.innerHTML = originalContent;
  }
}

function mountLightning() {
  const container = document.getElementById('lab-lightning-root');
  if (!container) return;

  try {
    const hasCursor =
      typeof window !== 'undefined' &&
      window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      container.remove();
      return;
    }

    const root = createRoot(container);
    root.render(
      <Lightning
        color="#E2A3B7"
        bolts={1}
        branches={0.28}
        angle={0}
        size={0.85}
        thickness={0.8}
        glow={1.05}
        intensity={0.8}
        speed={0.28}
        flicker={0.25}
        mouseInteraction={hasCursor}
        mouseStrength={0.35}
        clickStrike={false}
        intro={true}
        fade={0.3}
        opacity={0.65}
        lightMode={false}
        dpr={1.5}
      />
    );
  } catch (err) {
    console.warn('[THIN] Falha ao inicializar Lightning canvas:', err);
    container.remove();
  }
}

function mountColorBends() {
  const container = document.getElementById('sobre-colorbends-root');
  if (!container) return;

  try {
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      container.remove();
      return;
    }

    const root = createRoot(container);
    root.render(
      <ColorBends
        colors={['#5A1827', '#873C48', '#2B1219', '#E2A3B7']}
        rotation={125}
        speed={0.15}
        transparent={true}
        autoRotate={0.35}
        scale={1.25}
        frequency={1.05}
        warpStrength={0.85}
        mouseInfluence={0.35}
        parallax={0.25}
        noise={0.04}
        iterations={1}
        intensity={1.25}
        bandWidth={3.5}
      />
    );
  } catch (err) {
    console.warn('[THIN] Falha ao inicializar ColorBends:', err);
    container.remove();
  }
}

function init() {
  mountMaskedHeading();
  mountLightning();
  mountColorBends();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
