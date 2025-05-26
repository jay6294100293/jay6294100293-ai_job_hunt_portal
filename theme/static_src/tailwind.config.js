// theme/static_src/tailwind.config.js
const defaultTheme = require('tailwindcss/defaultTheme'); // Make sure to require defaultTheme
const colors = require('tailwindcss/colors'); // Require colors for primary/secondary

module.exports = {
   content: [
      '../../templates/**/*.html',
      '../../**/templates/**/*.html',
      '../templates/**/*.html',
      '../../**/forms.py',
  ],
  darkMode: 'class',
  theme: {
      extend: {
          colors: {
              primary: colors.indigo, // Using Tailwind's indigo for primary
              secondary: colors.purple, // Using Tailwind's purple for secondary
              // You had specific shades defined, which is also great.
              // If you prefer your exact shades:
              // primary: {
              //     '50':  '#eef2ff', '100': '#e0e7ff', '200': '#c7d2fe', '300': '#a5b4fc',
              //     '400': '#818cf8', '500': '#6366f1', '600': '#4f46e5', '700': '#4338ca',
              //     '800': '#3730a3', '900': '#312e81', '950': '#1e1b4b'
              // },
              // secondary: {
              //     '50':  '#faf5ff', '100': '#f3e8ff', '200': '#e9d5ff', '300': '#d8b4fe',
              //     '400': '#c084fc', '500': '#a855f7', '600': '#9333ea', '700': '#7e22ce',
              //     '800': '#6b21a8', '900': '#581c87', '950': '#2e1065'
              // },
          },
          fontFamily: {
              // Set 'Outfit' as the primary sans-serif font.
              // 'Plus Jakarta Sans' can be used with font-jakarta if needed, or also added to sans stack.
              sans: ['Outfit', ...defaultTheme.fontFamily.sans],
              jakarta: ['"Plus Jakarta Sans"', ...defaultTheme.fontFamily.sans],
          },
      },
  },
  plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/aspect-ratio'),
      require('@tailwindcss/line-clamp'),
  ],
}

// // theme/static_src/tailwind.config.js
// module.exports = {
//    content: [
//       // Scans templates in the project 'templates/' dir
//       '../../templates/**/*.html',
//       // Scans templates in any app 'templates/' dir (e.g., auth_app, job_portal)
//       '../../**/templates/**/*.html',
//       // Scans templates in the 'theme/templates/' dir (if used)
//       '../templates/**/*.html',
//       // Scans Python form files for classes
//       '../../**/forms.py',
//   ],
//   // --- ADD THIS LINE ---
//   darkMode: 'class', // Strategy: Use 'class' to toggle dark mode via HTML class, not OS setting
//   // --------------------
//   theme: {
//       extend: { // <-- Extend the theme here
//           colors: { // <-- Define custom colors
//               primary: { // Indigo shades
//                   '50':  '#eef2ff',
//                   '100': '#e0e7ff',
//                   '200': '#c7d2fe',
//                   '300': '#a5b4fc',
//                   '400': '#818cf8',
//                   '500': '#6366f1',
//                   '600': '#4f46e5',
//                   '700': '#4338ca', // Your desired base primary
//                   '800': '#3730a3',
//                   '900': '#312e81',
//                   '950': '#1e1b4b'
//               },
//               secondary: { // Purple shades
//                   '50':  '#f5f3ff',
//                   '100': '#ede9fe',
//                   '200': '#ddd6fe',
//                   '300': '#c4b5fd',
//                   '400': '#a78bfa',
//                   '500': '#8b5cf6',
//                   '600': '#7c3aed',
//                   '700': '#6d28d9',
//                   '800': '#5b21b6',
//                   '900': '#4c1d95',
//                   '950': '#2e1065'
//               },
//               accent: { // Cyan shades
//                   '50':  '#ecfeff',
//                   '100': '#cffafe',
//                   '200': '#a5f3fc',
//                   '300': '#67e8f9',
//                   '400': '#22d3ee',
//                   '500': '#06b6d4', // Your desired accent
//                   '600': '#0891b2',
//                   '700': '#0e7490',
//                   '800': '#155e75',
//                   '900': '#164e63',
//                   '950': '#083344'
//               },
//           },
//           fontFamily: {
//               sans: ['"Plus Jakarta Sans"', 'sans-serif'], // Default body font
//               heading: ['"Outfit"', 'sans-serif']          // Heading font
//           },
//           boxShadow: { // Adding shadows used in globals.css for clarity
//               'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', // Roughly shadow-md
//               'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', // Roughly shadow-lg
//               // You can add more custom shadows if needed
//           }
//       },
//   },
//   plugins: [
//       // Standard Tailwind plugins:
//       require('@tailwindcss/forms'),
//       require('@tailwindcss/typography'),
//       require('@tailwindcss/line-clamp'),
//       require('@tailwindcss/aspect-ratio'),
//       // Make sure 'require("daisyui")' is NOT present
//   ],
//   // Make sure the 'daisyui: { ... }' configuration block is completely removed
// }
//
//
// // // theme/static_src/tailwind.config.js
// // module.exports = {
// //    content: [
// //       // Scans templates in the project 'templates/' dir
// //       '../../templates/**/*.html',
// //       // Scans templates in any app 'templates/' dir (e.g., auth_app, job_portal)
// //       '../../**/templates/**/*.html',
// //       // Scans templates in the 'theme/templates/' dir (if used)
// //       '../templates/**/*.html',
// //       // Scans Python form files for classes
// //       '../../**/forms.py',
// //   ],
// //   theme: {
// //       extend: { // <-- Extend the theme here
// //           colors: { // <-- Define custom colors
// //               primary: { // Indigo shades
// //                   '50':  '#eef2ff',
// //                   '100': '#e0e7ff',
// //                   '200': '#c7d2fe',
// //                   '300': '#a5b4fc',
// //                   '400': '#818cf8',
// //                   '500': '#6366f1',
// //                   '600': '#4f46e5',
// //                   '700': '#4338ca', // Your desired base primary
// //                   '800': '#3730a3',
// //                   '900': '#312e81',
// //                   '950': '#1e1b4b'
// //               },
// //               secondary: { // Purple shades
// //                   '50':  '#f5f3ff',
// //                   '100': '#ede9fe',
// //                   '200': '#ddd6fe',
// //                   '300': '#c4b5fd',
// //                   '400': '#a78bfa',
// //                   '500': '#8b5cf6',
// //                   '600': '#7c3aed',
// //                   '700': '#6d28d9',
// //                   '800': '#5b21b6',
// //                   '900': '#4c1d95',
// //                   '950': '#2e1065'
// //               },
// //               accent: { // Cyan shades
// //                   '50':  '#ecfeff',
// //                   '100': '#cffafe',
// //                   '200': '#a5f3fc',
// //                   '300': '#67e8f9',
// //                   '400': '#22d3ee',
// //                   '500': '#06b6d4', // Your desired accent
// //                   '600': '#0891b2',
// //                   '700': '#0e7490',
// //                   '800': '#155e75',
// //                   '900': '#164e63',
// //                   '950': '#083344'
// //               },
// //           },
// //           fontFamily: {
// //               sans: ['"Plus Jakarta Sans"', 'sans-serif'], // Default body font
// //               heading: ['"Outfit"', 'sans-serif']          // Heading font
// //           },
// //           boxShadow: { // Adding shadows used in globals.css for clarity
// //               'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', // Roughly shadow-md
// //               'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', // Roughly shadow-lg
// //               // You can add more custom shadows if needed
// //           }
// //       },
// //   },
// //   plugins: [
// //       // Standard Tailwind plugins:
// //       require('@tailwindcss/forms'),
// //       require('@tailwindcss/typography'),
// //       require('@tailwindcss/line-clamp'),
// //       require('@tailwindcss/aspect-ratio'),
// //       // Make sure 'require("daisyui")' is NOT present
// //   ],
// //   // Make sure the 'daisyui: { ... }' configuration block is completely removed
// // }