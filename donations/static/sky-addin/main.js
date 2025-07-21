(function() {
  const client = new BBSkyAddinClient.AddinClient({
    callbacks: {
      init: async function(args) {
        args.ready({ showUI: true, title: 'Decline Event' });

        // 1) grab our SSO token for the backend
        const identityToken = await client.getUserIdentityToken();
        console.log("[main] identityToken:", identityToken.slice(0,10));
        const envid = args.envId;

        // 2) listen for the popup to postMessage us back
        let skyApiToken = null;
        window.addEventListener("message", e => {
          if (e.origin === window.location.origin && e.data.accessToken) {
            skyApiToken = e.data.accessToken;
            console.log("[main] got skyApiToken from popup:", skyApiToken.slice(0,10));
            loadEvents();
          }
        });

        // 3) wire up the “Connect” button
        document.getElementById('connect').addEventListener('click', () => {
          console.log("[main] opening authorize popup…");
          const popup = window.open(
            `/skyapi/authorize?token=${encodeURIComponent(identityToken)}&envid=${encodeURIComponent(envid)}`,
            "_blank","toolbar=0,status=0,width=600,height=500"
          );
          const iv = setInterval(async () => {
            if (popup.closed) {
              clearInterval(iv);
              const resp = await fetch('/skyapi/token', { credentials: 'include' });
              if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
              const { accessToken } = await resp.json();
              skyApiToken = accessToken;
              await loadEvents();
            }
          }, 100);
          });



        // 4) helper to load events once we have skyApiToken
        async function skyFetch(path, opts={}) {
          if (!skyApiToken) throw new Error("Missing SKY API token");
          const res = await fetch("https://api.sky.blackbaud.com" + path, {
            ...opts,
            headers: {
              Authorization: `Bearer ${skyApiToken}`,
              'Bb-Api-Subscription-Key': SUBSCRIPTION_KEY,
              'Content-Type': 'application/json'
            }
          });
          if (!res.ok) {
            const text = await res.text();
            console.error("[main] skyFetch failed", res.status, text);
            throw new Error(text);
          }
          return res.json();
        }

        async function loadEvents() {
          console.log("[main] loading events…");
          try {
            const { value: events } = await skyFetch('/event/v1/events');
            // …populate your dropdown…
          } catch (err) {
            console.error("[main] loadEvents error", err);
          }
        }
      }
    }
  });
})();
