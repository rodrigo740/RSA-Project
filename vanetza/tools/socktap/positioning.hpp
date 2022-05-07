#ifndef POSITIONING_HPP_VZRIW7PB
#define POSITIONING_HPP_VZRIW7PB

#include <vanetza/common/position_provider.hpp>
#include <vanetza/common/runtime.hpp>
#include <boost/asio/io_service.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/variables_map.hpp>
#include <memory>
#include <stdexcept>
#include "config.hpp"

class PositioningException : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};

std::unique_ptr<vanetza::PositionProvider>
create_position_provider(boost::asio::io_service&, config_t config_s, const vanetza::Runtime&);

#endif /* POSITIONING_HPP_VZRIW7PB */
