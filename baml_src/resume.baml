// Defining a data model.
class Resume {
  name string[]
  email string
  experience Experience[]
  skills string[]
}

class Experience {
  company string @description(#"
    Legal entity name (if not specified, use the generally understood company name)
  "#)
  title string
}

// Create a function to extract the resume from a string.
function ExtractResume(resume: string | image) -> Resume {
  client "openai/gpt-4o"
  prompt #"
    {{ _.role('user') }}

    Extract from this content:
        
    ---------------
    {{ resume }}
    ---------------
    {{ ctx.output_format }}
  "#
}

// Test the function with a sample resume. Open the VSCode playground to run this.
test vaibhav_resume {
  functions [ExtractResume]
  args {
    resume #"
      Vaibhav Gupta
      vbv@boundaryml.com

      Experience:
      - Founder at BoundaryML
      - CV Engineer at Google
      - CV Engineer at Microsoft

      Skills:
      - Rust
      - C++
    "#
  }
}

test vaibhav_resume_image {
  functions [ExtractResume]
  args {
    resume {
      file "resume.png"
    }
  }
}
