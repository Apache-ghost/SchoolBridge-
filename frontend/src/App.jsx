import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Modern Homepage Component
const Homepage = () => (
  <div style={{ minHeight: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
    {/* Navigation Header */}
    <nav style={{
      padding: '1rem 2rem',
      background: 'rgba(255,255,255,0.95)',
      backdropFilter: 'blur(10px)',
      position: 'fixed',
      top: 0,
      width: '100%',
      zIndex: 1000,
      borderBottom: '1px solid rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px' }}>🏫</span>
          <h1 style={{ margin: 0, color: '#2D3748', fontSize: '24px', fontWeight: '700' }}>SchoolBridge</h1>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <button style={{
            padding: '8px 20px',
            background: 'transparent',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: '#4F46E5',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            Teacher Login
          </button>
          <button style={{
            padding: '8px 20px',
            background: '#4F46E5',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: 'white',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            Student Login
          </button>
        </div>
      </div>
    </nav>

    {/* Hero Section */}
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '120px 2rem 80px',
      textAlign: 'center'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{
          fontSize: '52px',
          fontWeight: '800',
          margin: '0 0 20px 0',
          lineHeight: '1.1'
        }}>
          Every Child Connected. <br />Every Parent Informed.
        </h1>
        <p style={{
          fontSize: '22px',
          margin: '0 0 40px 0',
          opacity: '0.95',
          lineHeight: '1.5',
          maxWidth: '700px',
          margin: '0 auto 40px auto'
        }}>
          SchoolBridge brings African families closer to education through instant messaging, attendance alerts, and multilingual support that works on any device.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button style={{
            padding: '15px 40px',
            background: 'white',
            color: '#4F46E5',
            border: 'none',
            borderRadius: '30px',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
          }}>
            Get Started Today
          </button>
          <button style={{
            padding: '15px 40px',
            background: 'transparent',
            color: 'white',
            border: '2px solid white',
            borderRadius: '30px',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            Watch Demo
          </button>
        </div>
      </div>
    </div>

    {/* Features Section */}
    <div style={{ padding: '80px 2rem', background: '#F7FAFC' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '36px',
          fontWeight: '700',
          color: '#2D3748',
          marginBottom: '20px'
        }}>
          Built for African Schools
        </h2>
        <p style={{
          textAlign: 'center',
          fontSize: '18px',
          color: '#718096',
          marginBottom: '60px',
          maxWidth: '600px',
          margin: '0 auto 60px auto'
        }}>
          Understanding the unique challenges of education in Africa, we've built features that work even with limited connectivity.
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '40px',
          marginTop: '40px'
        }}>
          {/* Feature 1 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>📱</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Works Everywhere</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              From Lagos to Nairobi, reach every parent with SMS, WhatsApp, or our mobile app. No smartphone? No problem.
            </p>
          </div>

          {/* Feature 2 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #10B981, #059669)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>⚡</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Instant Alerts</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              "Your child is absent today." Parents know immediately, reducing absenteeism across African schools by 40%.
            </p>
          </div>

          {/* Feature 3 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #F59E0B, #D97706)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>🌍</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Speak Local</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              English, Français, Kiswahili, العربية, Hausa, Yoruba, Amharic. Communication in the language families understand.
            </p>
          </div>

          {/* Feature 4 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #EF4444, #DC2626)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>🎓</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Built for Africa</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              Low bandwidth? Rural areas? We've designed every feature to work reliably across the African continent.
            </p>
          </div>

          {/* Feature 5 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>💰</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Affordable</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              Starting at $1 per student per month. Making quality education communication accessible to every African school.
            </p>
          </div>

          {/* Feature 6 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #06B6D4, #0891B2)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px auto',
              fontSize: '36px'
            }}>👨‍👩‍👧‍👦</div>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '15px' }}>Family First</h3>
            <p style={{ color: '#4A5568', lineHeight: '1.7', fontSize: '16px' }}>
              Connect extended families, guardians, and caregivers. Understanding African family structures.
            </p>
          </div>
        </div>
      </div>
    </div>

    {/* Stats Section */}
    <div style={{ 
      padding: '100px 2rem', 
      background: 'linear-gradient(135deg, #1E40AF, #7C3AED)',
      color: 'white'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
        <h2 style={{ 
          fontSize: '42px', 
          fontWeight: '800', 
          marginBottom: '20px',
          background: 'linear-gradient(45deg, #FBBF24, #F59E0B)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Transforming Education Across Africa
        </h2>
        <p style={{ 
          fontSize: '20px', 
          marginBottom: '60px', 
          opacity: '0.9',
          maxWidth: '700px',
          margin: '0 auto 60px auto'
        }}>
          From Cape Town to Cairo, SchoolBridge is connecting families and improving student outcomes
        </p>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '50px'
        }}>
          <div style={{ 
            background: 'rgba(255,255,255,0.1)',
            padding: '40px 20px',
            borderRadius: '20px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ fontSize: '56px', fontWeight: '800', color: '#FBBF24', marginBottom: '10px' }}>2,500+</div>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '5px' }}>Schools Connected</div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Across 28 African countries</div>
          </div>
          <div style={{ 
            background: 'rgba(255,255,255,0.1)',
            padding: '40px 20px',
            borderRadius: '20px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ fontSize: '56px', fontWeight: '800', color: '#10B981', marginBottom: '10px' }}>750K+</div>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '5px' }}>Parents Reached</div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Active family connections</div>
          </div>
          <div style={{ 
            background: 'rgba(255,255,255,0.1)',
            padding: '40px 20px',
            borderRadius: '20px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ fontSize: '56px', fontWeight: '800', color: '#F59E0B', marginBottom: '10px' }}>40%</div>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '5px' }}>Less Absenteeism</div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Through instant alerts</div>
          </div>
          <div style={{ 
            background: 'rgba(255,255,255,0.1)',
            padding: '40px 20px',
            borderRadius: '20px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <div style={{ fontSize: '56px', fontWeight: '800', color: '#EF4444', marginBottom: '10px' }}>12+</div>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '5px' }}>Languages</div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Native communication</div>
          </div>
        </div>
      </div>
    </div>

    {/* Testimonials Section */}
    <div style={{ padding: '100px 2rem', background: '#F8FAFC' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ 
          textAlign: 'center', 
          fontSize: '42px', 
          fontWeight: '800', 
          color: '#1A202C', 
          marginBottom: '60px' 
        }}>
          Voices from African Schools
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '40px'
        }}>
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ marginBottom: '25px' }}>
              {"⭐".repeat(5)}
            </div>
            <p style={{ 
              fontSize: '18px', 
              lineHeight: '1.7', 
              color: '#2D3748', 
              marginBottom: '25px',
              fontStyle: 'italic'
            }}>
              "SchoolBridge transformed how we connect with parents. Our attendance improved by 35% when parents started receiving instant SMS alerts about their children."
            </p>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '700',
                marginRight: '15px'
              }}>
                MK
              </div>
              <div>
                <div style={{ fontWeight: '700', color: '#1A202C' }}>Mrs. Kemi Adebayo</div>
                <div style={{ color: '#718096', fontSize: '14px' }}>Principal, Lagos Primary School</div>
              </div>
            </div>
          </div>

          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ marginBottom: '25px' }}>
              {"⭐".repeat(5)}
            </div>
            <p style={{ 
              fontSize: '18px', 
              lineHeight: '1.7', 
              color: '#2D3748', 
              marginBottom: '25px',
              fontStyle: 'italic'
            }}>
              "Finally, a system that works with our reality. Parents without smartphones get SMS, others use WhatsApp. Everyone stays connected to their child's education."
            </p>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #10B981, #059669)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '700',
                marginRight: '15px'
              }}>
                JM
              </div>
              <div>
                <div style={{ fontWeight: '700', color: '#1A202C' }}>John Mwangi</div>
                <div style={{ color: '#718096', fontSize: '14px' }}>Head Teacher, Nairobi Community School</div>
              </div>
            </div>
          </div>

          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ marginBottom: '25px' }}>
              {"⭐".repeat(5)}
            </div>
            <p style={{ 
              fontSize: '18px', 
              lineHeight: '1.7', 
              color: '#2D3748', 
              marginBottom: '25px',
              fontStyle: 'italic'
            }}>
              "The multilingual support is incredible. Parents receive messages in Hausa, English, or French. No more language barriers preventing family engagement."
            </p>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: '700',
                marginRight: '15px'
              }}>
                FA
              </div>
              <div>
                <div style={{ fontWeight: '700', color: '#1A202C' }}>Fatima Al-Rashid</div>
                <div style={{ color: '#718096', fontSize: '14px' }}>Director, Kano International Academy</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* CTA Section */}
    <div style={{
      background: 'linear-gradient(135deg, #1A202C 0%, #2D3748 50%, #4A5568 100%)',
      color: 'white',
      padding: '120px 2rem',
      textAlign: 'center',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Pattern */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='m0 40l40-40h-40v40zm40 0v-40h-40l40 40z'/%3E%3C/g%3E%3C/svg%3E")`,
        opacity: 0.1
      }}></div>
      
      <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        <h2 style={{ 
          fontSize: '48px', 
          fontWeight: '800', 
          marginBottom: '25px',
          background: 'linear-gradient(45deg, #FBBF24, #F59E0B, #EF4444)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Transform Your School Today
        </h2>
        <p style={{ 
          fontSize: '22px', 
          marginBottom: '20px', 
          opacity: '0.9',
          lineHeight: '1.6'
        }}>
          Join 2,500+ African schools already bridging the communication gap
        </p>
        <p style={{ 
          fontSize: '18px', 
          marginBottom: '50px', 
          opacity: '0.8',
          color: '#FBBF24'
        }}>
          ✓ Free 30-day trial  ✓ No setup fees  ✓ Works on any device  ✓ 24/7 support in your language
        </p>
        
        <div style={{ 
          display: 'flex', 
          gap: '20px', 
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <button style={{
            padding: '18px 40px',
            background: 'linear-gradient(135deg, #10B981, #059669)',
            color: 'white',
            border: 'none',
            borderRadius: '50px',
            fontSize: '20px',
            fontWeight: '700',
            cursor: 'pointer',
            boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
            transition: 'all 0.3s ease'
          }}>
            🚀 Start Free Trial
          </button>
          <button style={{
            padding: '18px 40px',
            background: 'transparent',
            color: 'white',
            border: '2px solid white',
            borderRadius: '50px',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}>
            📅 Book Demo
          </button>
        </div>
        
        <div style={{ 
          marginTop: '60px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '40px',
          flexWrap: 'wrap',
          opacity: '0.7'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '14px', color: '#FBBF24' }}>Trusted by schools in</div>
            <div style={{ fontSize: '16px', fontWeight: '600' }}>Nigeria • Kenya • Ghana • Rwanda</div>
          </div>
        </div>
      </div>
    </div>

    {/* Footer */}
    <footer style={{ background: '#1A202C', color: 'white', padding: '60px 2rem 30px 2rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '40px',
          marginBottom: '40px'
        }}>
          <div>
            <h3 style={{ 
              fontSize: '24px', 
              fontWeight: '700', 
              marginBottom: '20px',
              background: 'linear-gradient(45deg, #FBBF24, #F59E0B)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              SchoolBridge
            </h3>
            <p style={{ opacity: '0.8', lineHeight: '1.6', marginBottom: '20px' }}>
              Bridging the communication gap in African education, one message at a time.
            </p>
            <div style={{ display: 'flex', gap: '15px' }}>
              <div style={{ fontSize: '24px', cursor: 'pointer' }}>🐦</div>
              <div style={{ fontSize: '24px', cursor: 'pointer' }}>📘</div>
              <div style={{ fontSize: '24px', cursor: 'pointer' }}>💼</div>
              <div style={{ fontSize: '24px', cursor: 'pointer' }}>📱</div>
            </div>
          </div>
          
          <div>
            <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>Product</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Features</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Pricing</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Mobile App</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Integrations</a></li>
            </ul>
          </div>
          
          <div>
            <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>Support</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Help Center</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Contact Us</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>Training</a></li>
              <li style={{ marginBottom: '10px' }}><a href="#" style={{ color: 'white', opacity: '0.8', textDecoration: 'none' }}>WhatsApp Support</a></li>
            </ul>
          </div>
          
          <div>
            <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px' }}>African Offices</h4>
            <div style={{ opacity: '0.8', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '10px' }}>🇳🇬 Lagos, Nigeria</div>
              <div style={{ marginBottom: '10px' }}>🇰🇪 Nairobi, Kenya</div>
              <div style={{ marginBottom: '10px' }}>🇬🇭 Accra, Ghana</div>
              <div style={{ marginBottom: '10px' }}>🇷🇼 Kigali, Rwanda</div>
            </div>
          </div>
        </div>
        
        <div style={{ 
          borderTop: '1px solid #4A5568', 
          paddingTop: '30px', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px'
        }}>
          <div style={{ opacity: '0.7' }}>
            © 2025 SchoolBridge. Proudly connecting African schools with modern technology.
          </div>
          <div style={{ display: 'flex', gap: '30px', flexWrap: 'wrap' }}>
            <a href="#" style={{ color: 'white', opacity: '0.7', textDecoration: 'none', fontSize: '14px' }}>Privacy Policy</a>
            <a href="#" style={{ color: 'white', opacity: '0.7', textDecoration: 'none', fontSize: '14px' }}>Terms of Service</a>
            <a href="#" style={{ color: 'white', opacity: '0.7', textDecoration: 'none', fontSize: '14px' }}>Data Protection</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
)

const TeacherDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👨‍🏫 Teacher Dashboard</h2>
    <p>Send communications to parents</p>
  </div>
)

const AdminDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👩‍💼 Admin Dashboard</h2>
    <p>Manage school operations</p>
  </div>
)

const StudentDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👨‍🎓 Student Dashboard</h2>
    <p>View assignments and grades</p>
  </div>
)

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/teacher" element={<TeacherDashboard />} />
        <Route path="/student" element={<StudentDashboard />} />
      </Routes>
    </Router>
  )
}

export default App