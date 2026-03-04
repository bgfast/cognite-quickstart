<template>
  <!-- Global layer: no visible content, only injects styles -->
  <div aria-hidden="true" class="slidev-global-style-anchor" />
</template>

<style>
/* Content slides only (exclude cover) */
.slidev-layout:not([data-slidev-layout="cover"]) {
  background: linear-gradient(160deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%) !important;
}

.slidev-layout:not([data-slidev-layout="cover"]) h1 {
  color: #1e40af !important;
  font-weight: 700 !important;
  border-bottom: 3px solid #3b82f6;
  padding-bottom: 0.35em;
  margin-bottom: 0.5em;
}

.slidev-layout:not([data-slidev-layout="cover"]) h2 {
  color: #334155 !important;
  font-weight: 600 !important;
}

.slidev-layout:not([data-slidev-layout="cover"]) p,
.slidev-layout:not([data-slidev-layout="cover"]) li {
  color: #1e293b !important;
  line-height: 1.5;
}

.slidev-layout:not([data-slidev-layout="cover"]) ul {
  margin-top: 0.5em;
  padding-left: 1.25em;
}

.slidev-layout:not([data-slidev-layout="cover"]) li {
  margin-bottom: 0.4em;
}

.slidev-layout:not([data-slidev-layout="cover"]) strong {
  color: #1e40af;
}
</style>
