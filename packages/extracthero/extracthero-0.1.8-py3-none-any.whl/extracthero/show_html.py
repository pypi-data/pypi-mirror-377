# show_html.py

# python show_html.py

import webbrowser
import tempfile
import os

html_doc = """
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Example Store</title>
</head>
<body>
  <header>
    <h1>Example Store</h1>
    <nav>…site navigation…</nav>
  </header>

  <div class="promo-banner">
    <p>🔥 Flash Sale: Up to 50% off! 🔥</p>
  </div>

  <!-- Main hero product -->
  <section id="hero-product">
    <div class="product" data-role="hero">
      <h2 class="title">Wireless Keyboard Pro</h2>
      <p class="description">
        Ergonomic backlit keyboard with rechargeable battery and adjustable tilt.
      </p>
      <div class="prices">
        <span class="list-price">€59.99</span>
        <span class="current-price">€49.99</span>
      </div>
      <div class="reviews" data-rating="4.5">
        ★★★★☆
      </div>
      <span class="availability">In Stock</span>
      <ul class="features">
        <li>Bluetooth 5.0</li>
        <li>USB-C charging</li>
        <li>Full-size layout</li>
      </ul>
    </div>
  </section>

  <!-- Related / recommended products -->
  <section id="related-products">
    <h3>Customers also viewed</h3>
    <div class="product recommended">
      <h2 class="title">USB-C Hub</h2>
      <p class="description">
        6-in-1 hub with HDMI, Ethernet, SD-card reader and two USB-A ports.
      </p>
      <span class="current-price">€29.50</span>
      <span class="availability">Only 3 left!</span>
    </div>

    <div class="product recommended">
      <h2 class="title">Gaming Mouse</h2>
      <p>
        High-precision mouse with RGB lighting.
      </p>
      <div class="pricing">
        <span class="current-price">$35.00</span>
      </div>
      <span class="availability">Out of Stock</span>
    </div>
  </section>

  <!-- A non-product section to be pruned -->
  <aside class="newsletter-signup">
    <h4>Join our newsletter</h4>
    <form>…</form>
  </aside>

  <footer>
    <p>© 2025 Example Store</p>
  </footer>
</body>
</html>
"""

# write to a temp file
with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
    f.write(html_doc)
    path = f.name

# open it in your default browser
webbrowser.open('file://' + os.path.realpath(path))
print(f"Preview opened in browser: {path}")
