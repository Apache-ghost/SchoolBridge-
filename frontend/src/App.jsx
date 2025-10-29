import React, { useState } from 'react'
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
            padding: '10px 25px',
            background: 'transparent',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: '#4F46E5',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
            marginRight: '10px'
          }}>
            👨‍🏫 Teacher Login
          </button>
          <button style={{
            padding: '10px 25px',
            background: '#4F46E5',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: 'white',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            👨‍👩‍👧‍👦 Parent Access
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

const TeacherDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const TabButton = ({ id, label, icon, isActive, onClick }) => (
    <button
      onClick={onClick}
      style={{
        padding: '12px 20px',
        background: isActive ? '#4F46E5' : 'transparent',
        color: isActive ? 'white' : '#4F46E5',
        border: '2px solid #4F46E5',
        borderRadius: '8px',
        fontWeight: '600',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px'
      }}
    >
      {icon} {label}
    </button>
  );

  return (
    <div style={{ padding: '40px', background: '#F7FAFC', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '30px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1A202C', marginBottom: '10px' }}>
            👨‍🏫 Teacher Communication Hub
          </h1>
          <p style={{ color: '#718096', fontSize: '16px' }}>
            Manage all parent-teacher communications from one place
          </p>
        </div>

        {/* Navigation Tabs */}
        <div style={{ 
          display: 'flex', 
          gap: '15px', 
          marginBottom: '30px', 
          flexWrap: 'wrap',
          borderBottom: '1px solid #E2E8F0',
          paddingBottom: '20px'
        }}>
          <TabButton
            id="overview"
            label="Overview"
            icon="📊"
            isActive={activeTab === 'overview'}
            onClick={() => setActiveTab('overview')}
          />
          <TabButton
            id="attendance"
            label="Attendance Alerts"
            icon="📋"
            isActive={activeTab === 'attendance'}
            onClick={() => setActiveTab('attendance')}
          />
          <TabButton
            id="reports"
            label="Report Cards"
            icon="📄"
            isActive={activeTab === 'reports'}
            onClick={() => setActiveTab('reports')}
          />
          <TabButton
            id="fees"
            label="Fee Notifications"
            icon="💰"
            isActive={activeTab === 'fees'}
            onClick={() => setActiveTab('fees')}
          />
          <TabButton
            id="chat"
            label="Parent Chat"
            icon="💬"
            isActive={activeTab === 'chat'}
            onClick={() => setActiveTab('chat')}
          />
          <TabButton
            id="events"
            label="Event Broadcast"
            icon="📅"
            isActive={activeTab === 'events'}
            onClick={() => setActiveTab('events')}
          />
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {/* Quick Stats */}
            <div style={{
              background: 'white',
              padding: '30px',
              borderRadius: '15px',
              boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                Today's Activity
              </h3>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <span style={{ color: '#718096' }}>Messages Sent</span>
                <span style={{ fontSize: '24px', fontWeight: '700', color: '#4F46E5' }}>12</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <span style={{ color: '#718096' }}>Attendance Alerts</span>
                <span style={{ fontSize: '24px', fontWeight: '700', color: '#10B981' }}>8</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#718096' }}>Unread Replies</span>
                <span style={{ fontSize: '24px', fontWeight: '700', color: '#EF4444' }}>3</span>
              </div>
            </div>

            {/* Quick Actions */}
            <div style={{
              background: 'white',
              padding: '30px',
              borderRadius: '15px',
              boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                Quick Actions
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <button style={{
                  padding: '15px 20px',
                  background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}>
                  📋 Mark Class Attendance
                </button>
                <button style={{
                  padding: '15px 20px',
                  background: 'linear-gradient(135deg, #10B981, #059669)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}>
                  💬 Send Bulk Message
                </button>
                <button style={{
                  padding: '15px 20px',
                  background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}>
                  📅 Create Event
                </button>
              </div>
            </div>

            {/* Recent Messages */}
            <div style={{
              background: 'white',
              padding: '30px',
              borderRadius: '15px',
              boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
              gridColumn: 'span 2'
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                Recent Parent Messages
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {[
                  { parent: 'Mrs. Johnson', message: 'Thank you for the attendance alert!', time: '10 min ago', status: 'unread' },
                  { parent: 'Mr. Adebayo', message: 'Can we schedule a meeting about Emma?', time: '1 hour ago', status: 'unread' },
                  { parent: 'Ms. Okafor', message: 'Received the report card. Great progress!', time: '2 hours ago', status: 'read' }
                ].map((msg, index) => (
                  <div key={index} style={{
                    padding: '15px',
                    background: msg.status === 'unread' ? '#F0F9FF' : '#F9FAFB',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${msg.status === 'unread' ? '#4F46E5' : '#E5E7EB'}`
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontWeight: '600', color: '#1A202C' }}>{msg.parent}</span>
                      <span style={{ fontSize: '12px', color: '#718096' }}>{msg.time}</span>
                    </div>
                    <p style={{ color: '#4A5568', margin: 0 }}>{msg.message}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'attendance' && (
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '20px' }}>
              📋 Attendance Management
            </h3>
            <p style={{ color: '#718096', marginBottom: '30px' }}>
              Mark attendance and automatically notify parents via SMS and app notifications.
            </p>
            <button style={{
              padding: '15px 30px',
              background: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}>
              Start Attendance for Today
            </button>
          </div>
        )}

        {activeTab === 'reports' && (
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '20px' }}>
              📄 Report Card Distribution
            </h3>
            <p style={{ color: '#718096', marginBottom: '30px' }}>
              Upload and automatically deliver report cards to parents with instant notifications.
            </p>
            <button style={{
              padding: '15px 30px',
              background: '#F59E0B',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}>
              Upload Report Cards
            </button>
          </div>
        )}

        {activeTab === 'fees' && (
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '20px' }}>
              💰 Fee Notification Center
            </h3>
            <p style={{ color: '#718096', marginBottom: '30px' }}>
              Send fee reminders, overdue notices, and payment confirmations to parents.
            </p>
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
              <button style={{
                padding: '15px 25px',
                background: '#EF4444',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}>
                Send Fee Reminders
              </button>
              <button style={{
                padding: '15px 25px',
                background: '#10B981',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}>
                Confirm Payments
              </button>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '20px' }}>
              💬 Parent Communication Center
            </h3>
            <p style={{ color: '#718096', marginBottom: '30px' }}>
              Direct messaging with parents. All conversations are logged and accessible via SMS for parents without smartphones.
            </p>
            <button style={{
              padding: '15px 30px',
              background: '#4F46E5',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}>
              Open Chat Interface
            </button>
          </div>
        )}

        {activeTab === 'events' && (
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '20px' }}>
              📅 Event Broadcasting
            </h3>
            <p style={{ color: '#718096', marginBottom: '30px' }}>
              Create and broadcast school events, meetings, and announcements to all parents or specific classes.
            </p>
            <button style={{
              padding: '15px 30px',
              background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}>
              Create New Event
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const AdminDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👩‍💼 Admin Dashboard</h2>
    <p>Manage school operations</p>
  </div>
)

const ParentDashboard = () => (
  <div style={{ padding: '40px', background: '#F7FAFC', minHeight: '100vh' }}>
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#1A202C', marginBottom: '30px' }}>
        👨‍👩‍👧‍👦 Parent Dashboard
      </h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Messages */}
        <div style={{
          background: 'white',
          padding: '30px',
          borderRadius: '15px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#4F46E5', marginBottom: '15px' }}>
            💬 Messages from Teachers
          </h3>
          <p style={{ color: '#718096' }}>View and respond to messages from your child's teachers</p>
        </div>

        {/* Attendance */}
        <div style={{
          background: 'white',
          padding: '30px',
          borderRadius: '15px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#10B981', marginBottom: '15px' }}>
            📋 Attendance Updates
          </h3>
          <p style={{ color: '#718096' }}>Real-time attendance notifications and alerts</p>
        </div>

        {/* Report Cards */}
        <div style={{
          background: 'white',
          padding: '30px',
          borderRadius: '15px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#F59E0B', marginBottom: '15px' }}>
            📊 Report Cards
          </h3>
          <p style={{ color: '#718096' }}>Access your child's academic progress reports</p>
        </div>

        {/* Fee Notifications */}
        <div style={{
          background: 'white',
          padding: '30px',
          borderRadius: '15px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#EF4444', marginBottom: '15px' }}>
            💰 Fee Information
          </h3>
          <p style={{ color: '#718096' }}>Fee reminders and payment confirmations</p>
        </div>
      </div>
    </div>
  </div>
)

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/teacher" element={<TeacherDashboard />} />
        <Route path="/parent" element={<ParentDashboard />} />
      </Routes>
    </Router>
  )
}

export default App