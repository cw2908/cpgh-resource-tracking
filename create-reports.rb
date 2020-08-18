require "samanage"
require "parallel"

api_token = ARGV[0]
RESOURCE_TRACKING_FILENAME = "Resource Tracking Report #{DateTime.now.strftime("%b-%d-%Y %H%M")}.csv"
RELATED_INCIDENT_FILENAME = "Related Incidents Report #{DateTime.now.strftime("%b-%d-%Y %H%M")}.csv"
SAMANAGE = Samanage::Api.new(token: api_token)
DEFAULT_OPTIONS = {
  incident: nil,
  filename: "Report #{DateTime.now.strftime("%b-%d-%Y %H%M")}",
  samanage: SAMANAGE,
  time_track: nil
}

class BaseReport
  attr_reader :filename, :incident, :samanage
  def initialize(options: DEFAULT_OPTIONS)
    @filename = options[:filename]
    @incident = options[:incident]
    @samanage = options[:samanage]
  end

  def related_incidents
    return @related_incidents if @related_incidents

    Parallel.map(incident["incidents"]) do |related_incident|
      related_incident_id = related_incident["id"]
      samanage.find_incident(id: related_incident_id)[:data]
    end
  end

  def to_hsh
    {}
  end

  def write_row
    write_headers = !File.exist?(filename)
    CSV.open(filename, "a+", write_headers: write_headers, force_quotes: true, headers: to_hsh.keys) do |csv|
      csv << to_hsh.values
    end
  end
end

class ResourceTrackingReport < BaseReport
  attr_reader :time_track
  def initialize(options:)
    @filename = options[:filename]
    @incident = options[:incident]
    @samanage = options[:samanage]
    @time_track = options[:time_track]
  end
  def to_hsh
    {
      time_track_id: time_track["id"],
      time_track_name: time_track["name"],
      time_track_minutes: time_track["minutes"],
      time_track_creator_email: time_track.dig("creator", "email"),
      time_track_creator_name: time_track.dig("creator", "name"),
      time_track_created_at: time_track["created_at"],
      time_track_updated_at: time_track["updated_at"],
      time_track_parent_href: time_track.dig("parent", "href").to_s.split(".json").first.to_s.gsub("api", "app"),
      incident_id: incident["id"],
      incident_number:  incident["number"],
      incident_state:  incident["state"],
      incident_category: incident.dig("category", "name"),
      incident_subcategory: incident.dig("subcategory", "name"),
      incident_assignee_email: incident.dig("assignee", "email"),
      incident_assignee_name: incident.dig("assignee", "name"),
      incident_requester_email: incident.dig("requester", "email"),
      incident_requester_name: incident.dig("requester", "name"),
      incident_created_at: incident["created_at"],
      incident_updated_at: incident["updated_at"],
      incident_resource_tracking: incident["custom_fields_values"]
        .find { |cf| cf["name"] == "Resource Tracking (Executive)" }
        .to_h.dig("value"),
      incident_name: incident["name"],
      incident_href:  incident["href"].to_s.split(".json").first.to_s.gsub("api", "app"),
    }
  end
end

class RelatedIncidentReport < BaseReport
  attr_reader :time_tracks
  def initialize(options:)
    @filename = options[:filename]
    @incident = options[:incident]
    @samanage = options[:samanage]
    @time_tracks = options[:time_tracks]
  end
  def sum_of_time_tracks
    time_tracks.inject(0) { |sum, time_track| sum + time_track["minutes"].to_i }
  end
  def generate_incident_hsh(related_incident_data:)
    {
      parent_incident_id: @incident.dig("id"),
      parent_incident_number: @incident.dig("number"),
      parent_incident_total_time: sum_of_time_tracks,
      parent_incident_state: @incident.dig("state"),
      parent_incident_category: @incident.dig("category", "name"),
      parent_incident_subcategory: @incident.dig("subcategory", "name"),
      parent_incident_resource_tracking: @incident.dig("custom_fields_values").to_a
                    .find { |cf| cf["name"] == "Resource Tracking (Executive)" }
                    .to_h.dig("value"),
      parent_incident_assignee_email: @incident.dig("assignee", "email"),
      parent_incident_assignee_name: @incident.dig("assignee", "name"),
      parent_incident_requester_email: @incident.dig("requester", "email"),
      parent_incident_requester_name: @incident.dig("requester", "name"),
      parent_incident_created_at: @incident.dig("created_at"),
      parent_incident_updated_at: @incident.dig("updated_at"),
      parent_incident_name: @incident.dig("name"),
      parent_incident_href: @incident.dig("href").to_s.split(".json").first.to_s.gsub("api", "app"),
      child_incident_id:  related_incident_data.dig("id"),
      child_incident_number:  related_incident_data.dig("number"),
      child_incident_state:  related_incident_data.dig("state"),
      child_incident_category:  related_incident_data.dig("category", "name"),
      child_incident_subcategory:  related_incident_data.dig("subcategory", "name"),
      child_incident_resource_tracking: related_incident_data.dig("custom_fields_values").to_a
                    .find { |cf| cf["name"] == "Resource Tracking (Executive)" }
                    .to_h.dig("value"),
      child_incident_assignee_email:  related_incident_data.dig("assignee", "email"),
      child_incident_assignee_name:  related_incident_data.dig("assignee", "name"),
      child_incident_requester_email:  related_incident_data.dig("requester", "email"),
      child_incident_requester_name:  related_incident_data.dig("requester", "name"),
      child_incident_created_at:  related_incident_data.dig("created_at"),
      child_incident_updated_at:  related_incident_data.dig("updated_at"),
      child_incident_name:  related_incident_data.dig("name"),
      child_incident_href:  related_incident_data.dig("href").to_s.split(".json").first.to_s.gsub("api", "app"),
    }
  end


  def to_hsh
    related_incident = related_incidents[0].to_h
    generate_incident_hsh(related_incident_data: related_incident)
  end
end


# resource_tracking_report = ResourceTrackingReport.new()
SAMANAGE.incidents(options: { 'updated[]': 1, verbose: true }).each do |incident|
  # Get Time Entries
  time_tracks_path = "incidents/#{incident['id']}/time_tracks.json"
  time_tracks = SAMANAGE.execute(path: time_tracks_path)[:data]

  ## Related Incident Report
  related_incident_options = DEFAULT_OPTIONS.merge({
    filename: RELATED_INCIDENT_FILENAME,
    incident: incident,
    time_tracks: time_tracks,

  })
  related_incident_report = RelatedIncidentReport.new(options: related_incident_options)
  related_incident_report.write_row


  ## Time Tracks Report
  puts "Writing #{time_tracks.count} timetracks to #{incident['href'].split('.json').first.to_s.gsub('api', 'app')}"
  time_tracks.each do |time_track|
    opts = DEFAULT_OPTIONS.merge(
      filename: RESOURCE_TRACKING_FILENAME,
      time_track: time_track,
      incident: incident
    )
    resource_tracking_report = ResourceTrackingReport.new(options: opts)
    resource_tracking_report.write_row
  end
end
