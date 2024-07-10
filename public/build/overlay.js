import MicroModal from "/public/micromodal.min.js"

document.addEventListener('DOMContentLoaded', () => {
    MicroModal.init();

    const body = document.getElementsByTagName('body')[0]
    const root = document.getElementById('root')
   
    //  overlayの作成
    var overlay = document.createElement('div')

    overlay.id = "overlay"
    overlay.style.width = "100%"
    overlay.style.height = "100vh"
    overlay.style.backgroundSize = "contain"
    overlay.style.overflow = "hidden"

    overlay.style.zIndex = 1000
    overlay.style.position = "absolute"

    var iframe = document.createElement('iframe')
    iframe.src = "https://apol.co.jp/"
    iframe.width = "100%"
    iframe.height = "100%"
    iframe.allow = "fullscreen"
    iframe.setAttribute('frameBorder', 0);

    iframe.style.position = "absolute"

    // intro modal
    var intro_modal = document.createElement('div')
    intro_modal.id = "intro-modal";
    intro_modal.ariaHidden = true;
    intro_modal.insertAdjacentHTML("afterbegin", '<div class="overlay" tabindex="-1" data-micromodal-close><div role="dialog" aria-modal="true" aria-labelledby="intro-modal-title" ><header><h2 id="intro-modal-title">Modal Title</h2><button aria-label="Close modal" data-micromodal-close></button></header><div id="intro-modal-content">Modal Content</div></div></div>')

    // personal_info modal
    var personal_info_modal = document.createElement('div')
    personal_info_modal.id = "personal_info"


    var btn = document.createElement("button") 
    btn.style.width = "100px"
    btn.style.height = "75px"
    btn.style.position = "absolute"
    btn.style.right = "50px"
    btn.style.bottom = "50px"
    btn.dataset.micromodalTrigger="intro-modal"

    // btn.addEventListener("click", () => {
        // body.removeChild(overlay)        
    // })

    overlay.appendChild(iframe)
    overlay.appendChild(btn)
    body.insertBefore(overlay, root)
}, false)
