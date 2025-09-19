# #########################################################################################
# Build image with everything required to run the tools
# #########################################################################################

FROM registry.gitlab.com/atomiq-project/boss

# Copy the contents of the repository into the image
WORKDIR /git
COPY . herostools

# Install herostools in editable mode
RUN pip install --break-system-packages -e herostools

